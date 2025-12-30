#!/bin/bash
# Script para criar usuário admin no sistema web (Google Cloud Run)
# Execute no Google Cloud Shell: bash CRIAR_ADMIN_PRODUCAO.sh

echo "============================================================"
echo "CRIAR USUARIO ADMINISTRADOR - SISTEMA WEB (PRODUCAO)"
echo "============================================================"
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"

# Configurar projeto
echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

# Verificar qual imagem usar
echo ""
echo "🔍 Verificando imagens disponíveis..."
IMAGE_MONPEC="gcr.io/${PROJECT_ID}/monpec:latest"
IMAGE_SISTEMA="gcr.io/${PROJECT_ID}/sistema-rural:latest"

# Tentar detectar qual imagem existe (ou usar sistema-rural como padrão)
IMAGE_NAME=$IMAGE_SISTEMA
echo "📦 Usando imagem: $IMAGE_NAME"
echo ""

# Solicitar dados do usuário
echo "Digite as informações do usuário admin:"
read -p "Username (ou Enter para 'admin'): " USERNAME
USERNAME=${USERNAME:-admin}

read -p "Email (ou Enter para 'admin@monpec.com.br'): " EMAIL
EMAIL=${EMAIL:-admin@monpec.com.br}

read -sp "Senha (mínimo 12 caracteres): " PASSWORD
echo ""

if [ ${#PASSWORD} -lt 12 ]; then
    echo "❌ ERRO: A senha deve ter no mínimo 12 caracteres!"
    exit 1
fi

read -sp "Confirme a senha: " PASSWORD_CONFIRM
echo ""

if [ "$PASSWORD" != "$PASSWORD_CONFIRM" ]; then
    echo "❌ ERRO: As senhas não coincidem!"
    exit 1
fi

echo ""
echo "🚀 Criando Cloud Run Job para criar usuário admin..."
echo ""

# Nome do job
JOB_NAME="criar-admin-$(date +%s)"

# Deletar job anterior se existir
gcloud run jobs delete criar-admin --region=$REGION --quiet 2>/dev/null || true

# Criar job
# CORREÇÃO: Usar sh -c com cd /app para garantir que manage.py seja encontrado
gcloud run jobs create criar-admin \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,ADMIN_PASSWORD=$PASSWORD" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py garantir_admin --username $USERNAME --email $EMAIL --senha $PASSWORD" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

if [ $? -ne 0 ]; then
    echo "❌ ERRO ao criar o job. Tentando com imagem alternativa..."
    
    # Tentar com outra imagem
    if [ "$IMAGE_NAME" == "$IMAGE_SISTEMA" ]; then
        IMAGE_NAME=$IMAGE_MONPEC
    else
        IMAGE_NAME=$IMAGE_SISTEMA
    fi
    
    echo "📦 Tentando com imagem: $IMAGE_NAME"
    # CORREÇÃO: Usar sh -c com cd /app para garantir que manage.py seja encontrado
    gcloud run jobs create criar-admin \
      --region=$REGION \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,ADMIN_PASSWORD=$PASSWORD" \
      --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
      --command="sh" \
      --args="-c,cd /app && python manage.py garantir_admin --username $USERNAME --email $EMAIL --senha $PASSWORD" \
      --max-retries=1 \
      --memory=2Gi \
      --cpu=2
fi

if [ $? -ne 0 ]; then
    echo "❌ ERRO: Não foi possível criar o job. Verifique as configurações."
    exit 1
fi

echo ""
echo "✅ Job criado! Executando..."
echo "⏱️  Isso pode levar 1-3 minutos..."
echo ""

# Executar o job
gcloud run jobs execute criar-admin --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ SUCESSO! Usuário admin criado!"
    echo "============================================================"
    echo ""
    echo "📝 Credenciais:"
    echo "   Username: $USERNAME"
    echo "   Email: $EMAIL"
    echo "   Senha: ********"
    echo ""
    echo "🌐 Agora você pode fazer login em:"
    echo "   https://monpec.com.br/login/"
    echo ""
    echo "💡 Dica: Você pode deletar o job depois:"
    echo "   gcloud run jobs delete criar-admin --region=$REGION"
    echo ""
else
    echo ""
    echo "❌ ERRO ao executar o job. Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=criar-admin\" --limit=50"
    echo ""
    exit 1
fi

