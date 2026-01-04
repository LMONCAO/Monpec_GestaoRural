#!/bin/bash
# Script de Deploy Completo para Google Cloud Run
# Uso: ./scripts/deploy_cloud_run.sh

set -e  # Parar em caso de erro

echo "🚀 Iniciando deploy do Monpec Gestão Rural no Google Cloud Run..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variáveis (ajustar conforme necessário)
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"seu-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="monpec"
INSTANCE_NAME=${CLOUD_SQL_INSTANCE:-"monpec-db"}

echo -e "${YELLOW}📋 Configuração:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service: $SERVICE_NAME"
echo "  Cloud SQL Instance: $INSTANCE_NAME"
echo ""

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud SDK não está instalado!${NC}"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar se está autenticado
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️ Não autenticado no Google Cloud. Fazendo login...${NC}"
    gcloud auth login
fi

# Definir projeto
echo -e "${GREEN}✅ Definindo projeto: $PROJECT_ID${NC}"
gcloud config set project $PROJECT_ID

# Passo 1: Aplicar Migrations
echo -e "${GREEN}📦 Passo 1: Aplicando migrations...${NC}"
echo "Criando job de migrations..."

# Criar job de migrations (se não existir)
if ! gcloud run jobs describe migrate-db --region=$REGION &> /dev/null; then
    echo "Criando job de migrations..."
    gcloud run jobs create migrate-db \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --region $REGION \
        --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp \
        --add-cloudsql-instances $PROJECT_ID:$REGION:$INSTANCE_NAME \
        --command python \
        --args manage.py,migrate \
        --memory 512Mi \
        --timeout 600 \
        --max-retries 1 || echo "Job já existe ou erro ao criar"
else
    echo "Job de migrations já existe. Atualizando..."
    gcloud run jobs update migrate-db \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --region $REGION \
        --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp \
        --add-cloudsql-instances $PROJECT_ID:$REGION:$INSTANCE_NAME \
        --command python \
        --args manage.py,migrate \
        --memory 512Mi \
        --timeout 600 || true
fi

# Executar migrations
echo "Executando migrations..."
gcloud run jobs execute migrate-db --region=$REGION --wait || {
    echo -e "${YELLOW}⚠️ Erro ao executar migrations. Continuando com deploy...${NC}"
}

# Passo 2: Build da Imagem
echo -e "${GREEN}📦 Passo 2: Fazendo build da imagem Docker...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest || {
    echo -e "${RED}❌ Erro no build!${NC}"
    exit 1
}

# Passo 3: Deploy no Cloud Run
echo -e "${GREEN}🚀 Passo 3: Fazendo deploy no Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False \
    --add-cloudsql-instances $PROJECT_ID:$REGION:$INSTANCE_NAME \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080 || {
    echo -e "${RED}❌ Erro no deploy!${NC}"
    exit 1
}

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format 'value(status.url)')

echo -e "${GREEN}✅ Deploy concluído com sucesso!${NC}"
echo -e "${GREEN}🌐 URL do serviço: $SERVICE_URL${NC}"

# Passo 4: Verificar Status
echo -e "${GREEN}🔍 Passo 4: Verificando status...${NC}"
sleep 5
gcloud run services describe $SERVICE_NAME --region=$REGION --format="table(status.conditions[0].type,status.conditions[0].status)"

echo -e "${GREEN}✅ Deploy finalizado!${NC}"
echo -e "${YELLOW}📝 Próximos passos:${NC}"
echo "  1. Verificar logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo "  2. Testar site: curl $SERVICE_URL"
echo "  3. Configurar domínio customizado se necessário"


