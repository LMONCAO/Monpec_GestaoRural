#!/bin/bash
# Script simples para executar migrate, collectstatic e criar admin
# Execute: bash executar_migrate_simples.sh

echo "🔍 Verificando configuração do gcloud..."

# Verificar e autenticar se necessário
ACCOUNT=$(gcloud config get-value account 2>/dev/null)
if [ -z "$ACCOUNT" ]; then
    echo "⚠️ Nenhuma conta ativa detectada."
    echo "No Cloud Shell, a autenticação geralmente é automática."
    echo "Tentando usar Application Default Credentials..."
    
    # No Cloud Shell, geralmente não precisa de login explícito
    # Mas vamos tentar verificar se conseguimos continuar
    gcloud config get-value project > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "❌ Erro: Não foi possível acessar o gcloud."
        echo "Tente executar: gcloud auth application-default login"
        exit 1
    fi
else
    echo "✅ Conta ativa: $ACCOUNT"
fi

# Configurar projeto (necessário antes de executar builds)
echo "🔧 Configurando projeto..."
gcloud config set project monpec-sistema-rural 2>/dev/null || {
    echo "⚠️ Aviso: Não foi possível configurar o projeto via gcloud config."
    echo "Continuando mesmo assim (o projeto pode estar configurado pelo ambiente)..."
}

# Verificar se está configurado
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT" ]; then
    echo "⚠️ Projeto não configurado via gcloud config, mas continuando..."
    PROJECT="monpec-sistema-rural"
else
    echo "✅ Projeto configurado: $PROJECT"
fi

CONFIG_FILE="/tmp/cloudbuild-migrate.yaml"

# Criar arquivo de configuração
cat > "$CONFIG_FILE" <<'YAML'
steps:
- name: 'gcr.io/monpec-sistema-rural/sistema-rural:latest'
  entrypoint: 'sh'
  args:
  - '-c'
  - |
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')"
  env:
  - 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'
  - 'DB_NAME=monpec_db'
  - 'DB_USER=monpec_user'
  - 'DB_PASSWORD=L6171r12@@jjms'
  - 'CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db'
YAML

# Executar build
echo "Executando migrate, collectstatic e criação do admin..."
gcloud builds submit --config="$CONFIG_FILE" .

# Limpar
rm -f "$CONFIG_FILE"

echo "✅ Concluído!"

