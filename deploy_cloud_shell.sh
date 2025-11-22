#!/bin/bash
# Script de deploy para Google Cloud Shell
# Copie e cole este script inteiro no Cloud Shell

set -e

echo "🚀 MONPEC - Deploy no Google Cloud Run"
echo "========================================"
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="Monpec2025!"

# Verificar se está autenticado
echo "🔐 Verificando autenticação..."
gcloud auth list

# Configurar projeto
echo ""
echo "📋 Configurando projeto: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Habilitar APIs
echo ""
echo "🔧 Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com

# Verificar se está na pasta correta
echo ""
echo "📁 Verificando arquivos..."
if [ ! -f "manage.py" ]; then
    echo "⚠️  Arquivo manage.py não encontrado!"
    echo "   Certifique-se de estar na pasta do projeto"
    echo "   Execute: cd Monpec_GestaoRural (ou nome da sua pasta)"
    exit 1
fi

echo "✅ Arquivos encontrados!"

# Obter connection name do banco
echo ""
echo "🔗 Obtendo connection name do banco..."
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)" 2>/dev/null || echo "")
if [ -z "$CONNECTION_NAME" ]; then
    echo "⚠️  Instância de banco não encontrada: $DB_INSTANCE"
    echo "   Continuando sem banco..."
    USE_DB=false
else
    echo "✅ Connection Name: $CONNECTION_NAME"
    USE_DB=true
fi

# Gerar SECRET_KEY
echo ""
echo "🔑 Gerando SECRET_KEY..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "temp-secret-key-change-me")
echo "✅ SECRET_KEY gerada"

# Build da imagem
echo ""
echo "========================================"
echo "🔨 PASSO 1/2: Build da imagem Docker"
echo "========================================"
echo "⏳ Isso pode levar 10-15 minutos..."
echo ""

gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Erro no build. Verifique os logs acima."
    exit 1
fi

echo ""
echo "✅ Build concluído!"
echo ""

# Deploy
echo "========================================"
echo "🚀 PASSO 2/2: Deploy no Cloud Run"
echo "========================================"
echo "⏳ Isso pode levar 2-3 minutos..."
echo ""

if [ "$USE_DB" = true ]; then
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --add-cloudsql-instances $CONNECTION_NAME \
        --set-env-vars \
            DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
            DEBUG=False,\
            DB_NAME=$DB_NAME,\
            DB_USER=$DB_USER,\
            DB_PASSWORD=$DB_PASSWORD,\
            CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
            SECRET_KEY=$SECRET_KEY \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
else
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars \
            DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
            DEBUG=False,\
            SECRET_KEY=$SECRET_KEY \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
fi

if [ $? -ne 0 ]; then
    echo "❌ Erro no deploy. Verifique os logs acima."
    exit 1
fi

echo ""
echo "✅ Deploy concluído!"
echo ""

# Obter URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo "========================================"
echo "  ✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo ""
echo "🌐 URL do serviço:"
echo "   $SERVICE_URL"
echo ""
echo "📋 Próximos passos:"
echo "   1. Teste a URL no navegador"
echo "   2. Verifique a meta tag: $SERVICE_URL (Ctrl+U para ver código-fonte)"
echo "   3. Teste arquivo HTML: $SERVICE_URL/google40933139f3b0d469.html"
echo "   4. Verifique no Google Search Console usando esta URL"
echo ""
echo "📖 Para configurar domínio monpec.com.br depois:"
echo "   gcloud run domain-mappings create \\"
echo "       --service $SERVICE_NAME \\"
echo "       --domain monpec.com.br \\"
echo "       --region $REGION"
echo ""

