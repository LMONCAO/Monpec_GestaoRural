#!/bin/bash
# Script completo de deploy para Google Cloud Run
# Este script faz TUDO: setup inicial, deploy, configuração e migrações

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DEPLOY COMPLETO MONPEC - GCP${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERRO: gcloud CLI não está instalado!${NC}"
    exit 1
fi

# Obter projeto
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Nenhum projeto configurado.${NC}"
    gcloud projects list
    read -p "Digite o PROJECT_ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}Projeto: ${PROJECT_ID}${NC}"
echo ""

# Etapa 1: Habilitar APIs
echo -e "${YELLOW}[1/7] Habilitando APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable cloudresourcemanager.googleapis.com --quiet
echo -e "${GREEN}✓ APIs habilitadas${NC}"
echo ""

# Etapa 2: Verificar/Criar Cloud SQL
echo -e "${YELLOW}[2/7] Verificando banco de dados...${NC}"
DB_INSTANCE=$(gcloud sql instances list --format="value(name)" --filter="name:monpec*" 2>/dev/null | head -n 1)

if [ -z "$DB_INSTANCE" ]; then
    echo -e "${YELLOW}Nenhuma instância Cloud SQL encontrada.${NC}"
    read -p "Deseja criar agora? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        read -sp "Senha do root do PostgreSQL: " DB_ROOT_PASSWORD
        echo
        echo "Criando instância (isso pode levar alguns minutos)..."
        gcloud sql instances create monpec-db \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=us-central1 \
            --root-password=$DB_ROOT_PASSWORD
        
        # Criar banco e usuário
        echo "Criando banco de dados..."
        gcloud sql databases create monpec_db --instance=monpec-db
        read -sp "Senha para o usuário monpec_user: " DB_USER_PASSWORD
        echo
        gcloud sql users create monpec_user \
            --instance=monpec-db \
            --password=$DB_USER_PASSWORD
        
        DB_INSTANCE="monpec-db"
        echo -e "${GREEN}✓ Banco de dados criado${NC}"
    else
        echo -e "${RED}É necessário criar o banco de dados antes de continuar.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Instância encontrada: ${DB_INSTANCE}${NC}"
fi

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)" 2>/dev/null)
echo -e "${GREEN}Connection Name: ${CONNECTION_NAME}${NC}"
echo ""

# Etapa 3: Build e Deploy
echo -e "${YELLOW}[3/7] Fazendo build e deploy...${NC}"
echo "Isso pode levar alguns minutos..."
gcloud builds submit --config cloudbuild-config.yaml
echo -e "${GREEN}✓ Deploy concluído${NC}"
echo ""

# Etapa 4: Configurar variáveis de ambiente
echo -e "${YELLOW}[4/7] Configurando variáveis de ambiente...${NC}"
echo "Você precisará fornecer algumas informações:"
echo ""

# Gerar SECRET_KEY se não tiver
if command -v python &> /dev/null; then
    SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "")
fi

if [ -z "$SECRET_KEY" ]; then
    read -sp "SECRET_KEY do Django (ou pressione Enter para gerar): " SECRET_KEY
    echo
    if [ -z "$SECRET_KEY" ]; then
        echo -e "${YELLOW}Gerando SECRET_KEY...${NC}"
        SECRET_KEY=$(openssl rand -base64 50 2>/dev/null || echo "CHANGE_THIS_SECRET_KEY_$(date +%s)")
    fi
fi

read -p "DB_NAME [monpec_db]: " DB_NAME
DB_NAME=${DB_NAME:-monpec_db}
read -p "DB_USER [monpec_user]: " DB_USER
DB_USER=${DB_USER:-monpec_user}
read -sp "DB_PASSWORD: " DB_PASSWORD
echo ""
read -sp "MERCADOPAGO_ACCESS_TOKEN: " MERCADOPAGO_ACCESS_TOKEN
echo ""
read -sp "MERCADOPAGO_PUBLIC_KEY: " MERCADOPAGO_PUBLIC_KEY
echo ""
read -p "SITE_URL [https://monpec.com.br]: " SITE_URL
SITE_URL=${SITE_URL:-https://monpec.com.br}

echo ""
echo -e "${YELLOW}Configurando variáveis...${NC}"

gcloud run services update monpec \
  --region=us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
  --set-env-vars="SECRET_KEY=$SECRET_KEY" \
  --set-env-vars="DEBUG=False" \
  --set-env-vars="DB_NAME=$DB_NAME" \
  --set-env-vars="DB_USER=$DB_USER" \
  --set-env-vars="DB_PASSWORD=$DB_PASSWORD" \
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME" \
  --set-env-vars="MERCADOPAGO_ACCESS_TOKEN=$MERCADOPAGO_ACCESS_TOKEN" \
  --set-env-vars="MERCADOPAGO_PUBLIC_KEY=$MERCADOPAGO_PUBLIC_KEY" \
  --set-env-vars="MERCADOPAGO_SUCCESS_URL=$SITE_URL/assinaturas/sucesso/" \
  --set-env-vars="MERCADOPAGO_CANCEL_URL=$SITE_URL/assinaturas/cancelado/" \
  --set-env-vars="SITE_URL=$SITE_URL" \
  --set-env-vars="PAYMENT_GATEWAY_DEFAULT=mercadopago" \
  --set-env-vars="PYTHONUNBUFFERED=1" \
  --add-cloudsql-instances=$CONNECTION_NAME

echo -e "${GREEN}✓ Variáveis configuradas${NC}"
echo ""

# Etapa 5: Aplicar migrações
echo -e "${YELLOW}[5/7] Aplicando migrações...${NC}"

# Verificar se job existe
JOB_EXISTS=$(gcloud run jobs describe migrate-monpec --region=us-central1 2>/dev/null || echo "")

if [ -z "$JOB_EXISTS" ]; then
    echo "Criando job de migração..."
    gcloud run jobs create migrate-monpec \
      --image=gcr.io/$PROJECT_ID/monpec:latest \
      --region=us-central1 \
      --command=python \
      --args=manage.py,migrate \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
      --set-env-vars="SECRET_KEY=$SECRET_KEY" \
      --set-env-vars="DB_NAME=$DB_NAME" \
      --set-env-vars="DB_USER=$DB_USER" \
      --set-env-vars="DB_PASSWORD=$DB_PASSWORD" \
      --set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME" \
      --set-env-vars="PYTHONUNBUFFERED=1" \
      --add-cloudsql-instances=$CONNECTION_NAME \
      --max-retries=3 \
      --task-timeout=600
fi

echo "Executando migrações..."
gcloud run jobs execute migrate-monpec --region=us-central1 --wait
echo -e "${GREEN}✓ Migrações aplicadas${NC}"
echo ""

# Etapa 6: Obter URL do serviço
echo -e "${YELLOW}[6/7] Obtendo informações do serviço...${NC}"
SERVICE_URL=$(gcloud run services describe monpec --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "")
echo -e "${GREEN}✓ Serviço disponível${NC}"
echo ""

# Etapa 7: Resumo
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}URL do serviço:${NC} ${SERVICE_URL}"
echo ""
echo -e "${YELLOW}Próximos passos:${NC}"
echo ""
echo "1. Criar superusuário:"
echo "   Acesse: ${SERVICE_URL}/admin"
echo "   Ou use o script: ./criar-superusuario.sh"
echo ""
echo "2. Configurar domínio personalizado (opcional):"
echo "   gcloud run domain-mappings create \\"
echo "     --service=monpec \\"
echo "     --domain=monpec.com.br \\"
echo "     --region=us-central1"
echo ""
echo "3. Verificar logs:"
echo "   gcloud run services logs tail monpec --region=us-central1"
echo ""
echo "4. Acessar console:"
echo "   https://console.cloud.google.com/run/detail/us-central1/monpec"
echo ""
echo -e "${GREEN}Tudo pronto! Seu sistema está no ar! 🚀${NC}"
echo ""

