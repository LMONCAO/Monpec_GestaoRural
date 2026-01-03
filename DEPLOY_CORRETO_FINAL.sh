#!/bin/bash
# 🚀 DEPLOY CORRETO E TESTADO - GOOGLE CLOUD RUN
# Script completo e validado para deploy do sistema MONPEC

set -e  # Parar em caso de erro

# ==========================================
# CONFIGURAÇÕES
# ==========================================
PROJECT_ID="${PROJECT_ID:-monpec-sistema-rural}"
SERVICE_NAME="${SERVICE_NAME:-monpec}"
REGION="${REGION:-us-central1}"
DB_INSTANCE="${DB_INSTANCE:-monpec-db}"
DB_NAME="${DB_NAME:-monpec_db}"
DB_USER="${DB_USER:-monpec_user}"

# ⚠️ NUNCA deixe segredos hardcoded neste arquivo.
# Defina via variáveis de ambiente (ou use GitHub Secrets/Secret Manager).
DB_PASSWORD="${DB_PASSWORD:-}"
SECRET_KEY="${SECRET_KEY:-}"
DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-}"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  DEPLOY CORRETO - MONPEC${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Validar segredos (evita deploy "quebrado" por falta de env)
if [ -z "$DB_PASSWORD" ] || [ -z "$SECRET_KEY" ] || [ -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo -e "${RED}❌ ERRO: Segredos não definidos no ambiente!${NC}"
    echo "Defina antes de rodar:"
    echo "  export DB_PASSWORD='...'"
    echo "  export SECRET_KEY='...'"
    echo "  export DJANGO_SUPERUSER_PASSWORD='...'"
    echo ""
    echo "Dica: use o bootstrap em deploy/gcp/bootstrap_gcp.sh para gerar e configurar automaticamente."
    exit 1
fi

# ==========================================
# VALIDAÇÕES INICIAIS
# ==========================================
echo -e "${BLUE}[1/8] Validando ambiente...${NC}"

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ ERRO: manage.py não encontrado!${NC}"
    echo "Certifique-se de estar no diretório raiz do projeto Django."
    exit 1
fi

if [ ! -f "Dockerfile.prod" ]; then
    echo -e "${RED}❌ ERRO: Dockerfile.prod não encontrado!${NC}"
    exit 1
fi

if [ ! -f "requirements_producao.txt" ]; then
    echo -e "${RED}❌ ERRO: requirements_producao.txt não encontrado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Arquivos essenciais encontrados${NC}"
echo ""

# ==========================================
# CONFIGURAR PROJETO
# ==========================================
echo -e "${BLUE}[2/8] Configurando projeto Google Cloud...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Projeto configurado: $PROJECT_ID${NC}"
echo ""

# ==========================================
# HABILITAR APIs
# ==========================================
echo -e "${BLUE}[3/8] Habilitando APIs necessárias...${NC}"
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
echo -e "${GREEN}✅ APIs habilitadas${NC}"
echo ""

# ==========================================
# CRIAR TAG ÚNICA
# ==========================================
echo -e "${BLUE}[4/8] Criando tag única para a imagem...${NC}"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_NAME="gcr.io/$PROJECT_ID/sistema-rural"
IMAGE_TAG="$IMAGE_NAME:v$TIMESTAMP"
IMAGE_LATEST="$IMAGE_NAME:latest"

echo "Tag única: $IMAGE_TAG"
echo "Tag latest: $IMAGE_LATEST"
echo ""

# ==========================================
# BUILD DA IMAGEM (SEM CACHE)
# ==========================================
echo -e "${BLUE}[5/8] Fazendo build da imagem Docker...${NC}"
echo -e "${YELLOW}⚠️  Isso pode levar 15-25 minutos (sem cache)...${NC}"
echo ""

gcloud builds submit \
    --no-cache \
    --tag $IMAGE_TAG \
    --tag $IMAGE_LATEST \
    --timeout=3600 \
    .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERRO: Falha no build!${NC}"
    echo "Verifique os logs acima para mais detalhes."
    exit 1
fi

echo -e "${GREEN}✅ Build concluído com sucesso${NC}"
echo ""

# ==========================================
# DEPLOY NO CLOUD RUN
# ==========================================
echo -e "${BLUE}[6/8] Fazendo deploy no Cloud Run...${NC}"
echo -e "${YELLOW}⚠️  Isso pode levar 5-10 minutos...${NC}"
echo ""

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:$DB_INSTANCE \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$DB_INSTANCE,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --max-instances=10 \
    --min-instances=0 \
    --port=8080

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERRO: Falha no deploy!${NC}"
    echo "Verifique os logs acima para mais detalhes."
    exit 1
fi

echo -e "${GREEN}✅ Deploy concluído com sucesso${NC}"
echo ""

# ==========================================
# OBTER URL DO SERVIÇO
# ==========================================
echo -e "${BLUE}[7/8] Obtendo URL do serviço...${NC}"
sleep 10

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)" \
    --project=$PROJECT_ID 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    echo -e "${YELLOW}⚠️  Não foi possível obter a URL automaticamente${NC}"
    echo "Execute: gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'"
else
    echo -e "${GREEN}✅ URL obtida: $SERVICE_URL${NC}"
fi

echo ""

# ==========================================
# RESUMO FINAL
# ==========================================
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}📋 Informações do Deploy:${NC}"
echo "  Projeto: $PROJECT_ID"
echo "  Serviço: $SERVICE_NAME"
echo "  Região: $REGION"
echo "  Imagem: $IMAGE_TAG"
echo ""

if [ ! -z "$SERVICE_URL" ]; then
    echo -e "${GREEN}🌐 URL do Sistema:${NC}"
    echo "  $SERVICE_URL"
    echo ""
fi

echo -e "${YELLOW}⏳ Próximos Passos:${NC}"
echo "  1. Aguarde 1-2 minutos para o serviço inicializar completamente"
if [ ! -z "$SERVICE_URL" ]; then
    echo "  2. Acesse: $SERVICE_URL"
fi
echo "  3. Teste o login com:"
echo "     Usuário: admin"
echo "     Senha: $DJANGO_SUPERUSER_PASSWORD"
echo ""

echo -e "${BLUE}📊 Acompanhar o Deploy:${NC}"
echo "  - Builds: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo "  - Cloud Run: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID"
echo "  - Logs: https://console.cloud.google.com/logs/query?project=$PROJECT_ID"
echo ""

echo -e "${GREEN}✅ Deploy finalizado!${NC}"
echo ""
