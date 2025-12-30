#!/bin/bash
# Solução completa para executar migrate, collectstatic e criar admin
# Execute: bash SOLUCAO_COMPLETA_MIGRATE.sh

set -e  # Parar em caso de erro

echo "=== SOLUÇÃO COMPLETA PARA MIGRATE E COLECTSTATIC ==="
echo ""

# Configurar projeto
echo "1️⃣ Configurando projeto..."
gcloud config set project monpec-sistema-rural
echo "✅ Projeto configurado"
echo ""

# Criar arquivo de configuração
echo "2️⃣ Criando arquivo de configuração..."
CONFIG_FILE="/tmp/cloudbuild-migrate.yaml"

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

echo "✅ Arquivo criado: $CONFIG_FILE"
echo ""

# Verificar se o arquivo foi criado
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Erro: Arquivo não foi criado!"
    exit 1
fi

# Verificar autenticação antes de executar build
echo "3️⃣ Verificando autenticação..."
ACCOUNT=$(gcloud config get-value account 2>/dev/null)
if [ -z "$ACCOUNT" ]; then
    echo "⚠️ Nenhuma conta ativa detectada."
    echo "Tentando usar Application Default Credentials do Cloud Shell..."
    # No Cloud Shell, geralmente funciona mesmo sem conta explícita
    # Mas vamos tentar configurar Application Default Credentials
    gcloud auth application-default print-access-token > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "❌ Erro: Não foi possível obter credenciais."
        echo ""
        echo "💡 SOLUÇÃO ALTERNATIVA: Use Cloud Run Jobs (Opção 2 no arquivo COMANDOS_PARA_GOOGLE_CLOUD_SHELL.md)"
        echo "   Cloud Run Jobs funciona melhor e não depende de gcloud builds submit."
        exit 1
    fi
else
    echo "✅ Conta ativa: $ACCOUNT"
fi

# Executar build
echo ""
echo "4️⃣ Executando migrate, collectstatic e criação do admin..."
echo "⏱️ Isso pode levar 3-5 minutos..."
echo ""
gcloud builds submit --config="$CONFIG_FILE" . || {
    echo ""
    echo "❌ Erro ao executar gcloud builds submit."
    echo ""
    echo "💡 SOLUÇÃO: Use Cloud Run Jobs em vez de gcloud builds submit."
    echo "   Veja a 'OPÇÃO 2: Cloud Run Jobs' no arquivo COMANDOS_PARA_GOOGLE_CLOUD_SHELL.md"
    echo "   Cloud Run Jobs é mais confiável e tem acesso garantido ao Cloud SQL."
    exit 1
}

# Limpar
echo ""
echo "5️⃣ Limpando arquivo temporário..."
rm -f "$CONFIG_FILE"

echo ""
echo "✅✅✅ CONCLUÍDO COM SUCESSO! ✅✅✅"
echo ""
echo "Agora você pode:"
echo "- Acessar o sistema na URL do Cloud Run"
echo "- Fazer login com:"
echo "  Usuário: admin"
echo "  Senha: L6171r12@@"

