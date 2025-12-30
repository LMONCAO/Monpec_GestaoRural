#!/bin/bash
# 🚀 DEPLOY DIRETO NO GOOGLE CLOUD SHELL
# Script completo para fazer deploy direto pelo Google Cloud Shell
# Copie e cole este código no Google Cloud Shell

set -e  # Parar em caso de erro

# ==========================================
# CONFIGURAÇÕES
# ==========================================
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
DJANGO_SUPERUSER_PASSWORD="L6171r12@@"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DEPLOY DIRETO NO GOOGLE CLOUD${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ==========================================
# PASSO 1: CONFIGURAR PROJETO
# ==========================================
echo -e "${YELLOW}[1/7] Configurando projeto...${NC}"
gcloud config set project $PROJECT_ID
echo -e "${GREEN}✅ Projeto configurado${NC}"
echo ""

# ==========================================
# PASSO 2: HABILITAR APIs
# ==========================================
echo -e "${YELLOW}[2/7] Habilitando APIs necessárias...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable containerregistry.googleapis.com
echo -e "${GREEN}✅ APIs habilitadas${NC}"
echo ""

# ==========================================
# PASSO 3: VERIFICAR ARQUIVOS
# ==========================================
echo -e "${YELLOW}[3/7] Verificando arquivos necessários...${NC}"
if [ ! -f "Dockerfile.prod" ]; then
    echo "❌ ERRO: Dockerfile.prod não encontrado!"
    echo "Certifique-se de estar no diretório correto com todos os arquivos do projeto."
    exit 1
fi
if [ ! -f "requirements_producao.txt" ]; then
    echo "❌ ERRO: requirements_producao.txt não encontrado!"
    exit 1
fi
if [ ! -f "manage.py" ]; then
    echo "❌ ERRO: manage.py não encontrado!"
    echo "Certifique-se de estar no diretório raiz do projeto Django."
    exit 1
fi
echo -e "${GREEN}✅ Arquivos encontrados${NC}"
echo ""

# ==========================================
# PASSO 4: BUILD DA IMAGEM (SEM CACHE)
# ==========================================
echo -e "${YELLOW}[4/7] Fazendo build da imagem Docker (sem cache)...${NC}"
echo "Isso pode levar 15-25 minutos..."
echo ""

IMAGE_NAME="gcr.io/$PROJECT_ID/sistema-rural"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="$IMAGE_NAME:v$TIMESTAMP"
IMAGE_LATEST="$IMAGE_NAME:latest"

echo "Tag única: $IMAGE_TAG"
echo "Tag latest: $IMAGE_LATEST"
echo ""

gcloud builds submit --no-cache --tag $IMAGE_TAG --tag $IMAGE_LATEST .

if [ $? -ne 0 ]; then
    echo "❌ ERRO: Falha no build!"
    exit 1
fi

echo -e "${GREEN}✅ Build concluído${NC}"
echo ""

# ==========================================
# PASSO 5: DEPLOY NO CLOUD RUN
# ==========================================
echo -e "${YELLOW}[5/7] Fazendo deploy no Cloud Run...${NC}"
echo "Isso pode levar alguns minutos..."
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
    --min-instances=0

if [ $? -ne 0 ]; then
    echo "❌ ERRO: Falha no deploy!"
    exit 1
fi

echo -e "${GREEN}✅ Deploy concluído${NC}"
echo ""

# ==========================================
# PASSO 6: VERIFICAR STATUS
# ==========================================
echo -e "${YELLOW}[6/7] Verificando status do serviço...${NC}"
sleep 10

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)

if [ -z "$SERVICE_URL" ]; then
    echo "⚠️  Não foi possível obter a URL do serviço"
else
    echo -e "${GREEN}✅ Serviço disponível em: $SERVICE_URL${NC}"
fi
echo ""

# ==========================================
# PASSO 7: RESUMO FINAL
# ==========================================
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "📋 Informações:"
echo "  - Projeto: $PROJECT_ID"
echo "  - Serviço: $SERVICE_NAME"
echo "  - Região: $REGION"
echo "  - Imagem: $IMAGE_TAG"
echo ""

if [ ! -z "$SERVICE_URL" ]; then
    echo "🌐 URL do sistema:"
    echo "  $SERVICE_URL"
    echo ""
    echo "⏳ Aguarde 1-2 minutos para o serviço inicializar completamente"
    echo ""
    echo "🔐 Credenciais de admin:"
    echo "  Usuário: admin"
    echo "  Senha: $DJANGO_SUPERUSER_PASSWORD"
    echo ""
fi

echo "📊 Para acompanhar o deploy:"
echo "  - Builds: https://console.cloud.google.com/cloud-build/builds?project=$PROJECT_ID"
echo "  - Cloud Run: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME?project=$PROJECT_ID"
echo "  - Logs: https://console.cloud.google.com/logs/query?project=$PROJECT_ID"
echo ""

echo -e "${GREEN}✅ Deploy finalizado!${NC}"
echo ""

