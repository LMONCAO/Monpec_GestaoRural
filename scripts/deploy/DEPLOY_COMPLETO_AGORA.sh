#!/bin/bash
# Script Completo de Deploy para Google Cloud Run
# Execute no Google Cloud Shell
# Uso: bash DEPLOY_COMPLETO_AGORA.sh

set -e  # Parar em caso de erro

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_$1ap4+4t"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}🚀 DEPLOY COMPLETO - MONPEC${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ ERRO: manage.py não encontrado!${NC}"
    echo "Execute este script no diretório raiz do projeto."
    exit 1
fi

# 1. Configurar projeto
echo -e "${YELLOW}[1/6] Configurando projeto GCP...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Projeto configurado: $PROJECT_ID${NC}"
echo ""

# 2. Verificar autenticação
echo -e "${YELLOW}[2/6] Verificando autenticação...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Fazendo login...${NC}"
    gcloud auth login
fi
echo -e "${GREEN}✅ Autenticado${NC}"
echo ""

# 3. Habilitar APIs
echo -e "${YELLOW}[3/6] Habilitando APIs necessárias...${NC}"
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "sqladmin.googleapis.com"
)

for api in "${APIS[@]}"; do
    gcloud services enable "$api" --quiet 2>/dev/null || true
done
echo -e "${GREEN}✅ APIs habilitadas${NC}"
echo ""

# 4. Build da imagem Docker
echo -e "${YELLOW}[4/6] Buildando imagem Docker...${NC}"
echo -e "${CYAN}⏱️  Isso pode levar 5-10 minutos...${NC}"
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"
gcloud builds submit --tag $IMAGE_TAG
echo -e "${GREEN}✅ Build concluído!${NC}"
echo ""

# 5. Deploy no Cloud Run
echo -e "${YELLOW}[5/6] Deployando no Cloud Run...${NC}"
echo -e "${CYAN}⏱️  Isso pode levar 2-5 minutos...${NC}"

ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$DB_INSTANCE,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances="$PROJECT_ID:$REGION:$DB_INSTANCE" \
    --set-env-vars "$ENV_VARS" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --min-instances=1 \
    --max-instances=10 \
    --port=8080

echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""

# 6. Obter URL e informações
echo -e "${YELLOW}[6/6] Obtendo informações do serviço...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅✅✅ DEPLOY CONCLUÍDO COM SUCESSO! ✅✅✅${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}🔗 URL do Serviço:${NC}"
echo -e "${GREEN}   $SERVICE_URL${NC}"
echo ""
echo -e "${CYAN}📋 Próximos Passos:${NC}"
echo "   1. Aplicar migrações no Cloud SQL:"
echo "      gcloud run jobs create migrate-job \\"
echo "        --image $IMAGE_TAG \\"
echo "        --region $REGION \\"
echo "        --add-cloudsql-instances=\"$PROJECT_ID:$REGION:$DB_INSTANCE\" \\"
echo "        --set-env-vars=\"DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$DB_INSTANCE\" \\"
echo "        --command=\"python\" \\"
echo "        --args=\"manage.py,migrate\" \\"
echo "        --memory=2Gi \\"
echo "        --cpu=2"
echo ""
echo "   2. Criar superusuário (via admin ou job)"
echo ""
echo "   3. Testar sistema:"
echo "      - Acesse: $SERVICE_URL"
echo "      - Teste criação de usuário demo"
echo "      - Teste sistema de assinaturas"
echo ""
echo -e "${CYAN}📊 Ver Logs:${NC}"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50"
echo ""
echo -e "${CYAN}🔄 Atualizar Deploy:${NC}"
echo "   Execute este script novamente"
echo ""


