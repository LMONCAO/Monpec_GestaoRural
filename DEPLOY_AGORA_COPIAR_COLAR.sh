#!/bin/bash
# 🚀 DEPLOY RÁPIDO - Copie e cole este script completo no Cloud Shell
# Este script faz TUDO automaticamente

set -e

echo "🚀 MONPEC - Deploy Automático"
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

# Configurar projeto
echo "⚙️  Configurando projeto..."
gcloud config set project $PROJECT_ID

# Navegar para pasta
echo "📁 Navegando para pasta..."
cd ~
if [ ! -d "Monpec_GestaoRural" ]; then
    echo "📥 Clonando repositório..."
    git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
fi
cd ~/Monpec_GestaoRural

# Atualizar código
echo "📥 Atualizando código do GitHub..."
git pull origin master || git pull origin main
echo "✅ Código atualizado!"
echo ""

# Verificar arquivos
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Arquivo manage.py não encontrado!"
    exit 1
fi

# Obter connection name
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
echo ""

# Build da imagem
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
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" \
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
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY" \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
fi

if [ $? -ne 0 ]; then
    echo ""
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
echo "   1. Teste: $SERVICE_URL"
echo "   2. Verifique meta tag: $SERVICE_URL (Ctrl+U para ver código-fonte)"
echo ""
echo "🔍 Se houver erro, verifique os logs:"
echo "   gcloud run services logs read monpec --region us-central1 --limit 50"
echo ""














