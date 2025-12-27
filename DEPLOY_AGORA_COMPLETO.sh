#!/bin/bash
# Script completo de deploy para Google Cloud Run
# Este script faz tudo necessário para colocar o sistema em produção

set -e  # Parar em caso de erro

echo "🚀 =========================================="
echo "   DEPLOY COMPLETO - MONPEC"
echo "   Google Cloud Run"
echo "=========================================="
echo ""

# 1. Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Erro: gcloud CLI não está instalado!"
    echo "   Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# 2. Obter projeto atual
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ Erro: Nenhum projeto Google Cloud configurado!"
    echo "   Execute: gcloud config set project SEU_PROJECT_ID"
    exit 1
fi

echo "✅ Projeto: $PROJECT_ID"
echo ""

# 3. Configurações
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

# 4. Habilitar APIs necessárias
echo "📋 Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
echo "✅ APIs habilitadas"
echo ""

# 5. Verificar se Dockerfile existe
if [ ! -f "Dockerfile.prod" ]; then
    echo "❌ Erro: Dockerfile.prod não encontrado!"
    exit 1
fi

# 6. Build da imagem
echo "📦 Fazendo build da imagem Docker..."
echo "   Isso pode levar alguns minutos..."
gcloud builds submit --tag $IMAGE_NAME --timeout=1800s
echo "✅ Build concluído"
echo ""

# 7. Deploy no Cloud Run
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
    --set-env-vars="PYTHONUNBUFFERED=1"
echo "✅ Deploy concluído"
echo ""

# 8. Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null)
echo "🌐 URL do serviço: $SERVICE_URL"
echo ""

# 9. Verificar se precisa configurar variáveis de ambiente
echo "⚠️  IMPORTANTE: Configure as variáveis de ambiente necessárias:"
echo ""
echo "   gcloud run services update $SERVICE_NAME \\"
echo "     --region=$REGION \\"
echo "     --update-env-vars=\"SECRET_KEY=SUA_SECRET_KEY_AQUI\" \\"
echo "     --update-env-vars=\"DEBUG=False\" \\"
echo "     --update-env-vars=\"DB_NAME=monpec_db\" \\"
echo "     --update-env-vars=\"DB_USER=monpec_user\" \\"
echo "     --update-env-vars=\"DB_PASSWORD=SUA_SENHA_DB\" \\"
echo "     --update-env-vars=\"CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME\""
echo ""
echo "   Para ver todas as variáveis necessárias, consulte: DEPLOY_GCP_COMPLETO.md"
echo ""

# 10. Aplicar migrações (se necessário)
echo "📝 Para aplicar migrações, execute:"
echo "   gcloud run jobs create migrate \\"
echo "     --image $IMAGE_NAME \\"
echo "     --region $REGION \\"
echo "     --command python \\"
echo "     --args manage.py,migrate"
echo ""

echo "✅ =========================================="
echo "   DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=========================================="
echo ""
echo "🌐 Acesse: $SERVICE_URL"
echo ""









