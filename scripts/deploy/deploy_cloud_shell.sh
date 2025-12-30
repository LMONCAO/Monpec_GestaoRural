#!/bin/bash
# Script para Deploy no Google Cloud Shell
# Execute: bash DEPLOY_CLOUD_SHELL.sh

set -e  # Parar em caso de erro

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

echo "========================================"
echo "🚀 DEPLOY MONPEC - Google Cloud Run"
echo "========================================"
echo ""

# 1. Configurar projeto
echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID
echo ""

# 2. Corrigir senha do banco
echo "🔧 Corrigindo senha do banco..."
gcloud sql users set-password monpec_user --instance=monpec-db --password="$DB_PASSWORD" || echo "⚠️ Aviso: Não foi possível atualizar senha (pode ser normal)"
echo ""

# 3. Garantir openpyxl no requirements
echo "📦 Verificando requirements..."
if [ ! -f "requirements_producao.txt" ] || ! grep -q "^openpyxl" requirements_producao.txt; then
    echo "openpyxl>=3.1.5" >> requirements_producao.txt
    echo "✅ openpyxl adicionado"
fi
echo ""

# 4. Build
echo "🔨 Buildando imagem Docker (5-10 minutos)..."
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
gcloud builds submit --tag $IMAGE_TAG
echo "✅ Build concluído!"
echo ""

# 5. Deploy
echo "🚀 Deployando no Cloud Run (2-5 minutos)..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances="$PROJECT_ID:$REGION:monpec-db" \
    --set-env-vars "$ENV_VARS" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600

echo ""

# 6. Obter URL
echo "========================================"
echo "✅✅✅ DEPLOY CONCLUÍDO! ✅✅✅"
echo "========================================"
echo ""
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "🔗 URL do Serviço:"
echo "   $SERVICE_URL"
echo ""
echo "📋 Credenciais para Login:"
echo "   Username: admin"
echo "   Senha: L6171r12@@"
echo ""
echo "⏱️ Aguarde 1-2 minutos para o serviço inicializar completamente"
echo ""
