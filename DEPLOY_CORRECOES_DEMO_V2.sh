#!/bin/bash
# 🚀 DEPLOY CORREÇÕES USUÁRIO DEMO - VERSÃO MELHORADA
# Script com timeout aumentado e melhor tratamento de erros

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
DJANGO_SUPERUSER_PASSWORD="L6171r12@@"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  DEPLOY CORREÇÕES USUÁRIO DEMO (V2)${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ ERRO: manage.py não encontrado!${NC}"
    echo "Execute: cd ~/Monpec_GestaoRural"
    exit 1
fi

# Configurar projeto
gcloud config set project $PROJECT_ID --quiet

# Build
echo -e "${BLUE}[1/3] Fazendo build da imagem...${NC}"
IMAGE_NAME="gcr.io/$PROJECT_ID/sistema-rural"
gcloud builds submit --tag $IMAGE_NAME:latest --timeout=1800s .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro no build!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build concluído${NC}"
echo ""

# Deploy com timeout aumentado
echo -e "${BLUE}[2/3] Fazendo deploy no Cloud Run (com timeout aumentado)...${NC}"
CLOUD_SQL_CONN="$PROJECT_ID:$REGION:$DB_INSTANCE"

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=$CLOUD_SQL_CONN \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONN,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DEMO_USER_PASSWORD=monpec" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=900 \
    --max-instances=10 \
    --min-instances=0 \
    --cpu-boost

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro no deploy!${NC}"
    echo ""
    echo -e "${YELLOW}Verifique os logs:${NC}"
    echo "bash VERIFICAR_LOGS_DEPLOY.sh"
    echo ""
    echo "Ou acesse:"
    echo "https://console.cloud.google.com/logs/viewer?project=$PROJECT_ID&resource=cloud_run_revision/service_name=$SERVICE_NAME"
    exit 1
fi

# Obter URL
echo ""
echo -e "${BLUE}[3/3] Obtendo URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  DEPLOY CONCLUÍDO!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

if [ ! -z "$SERVICE_URL" ]; then
    echo -e "${GREEN}URL: $SERVICE_URL${NC}"
    echo ""
    echo "Aguarde 1-2 minutos e teste o login com usuário demo"
fi

echo ""

