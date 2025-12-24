#!/bin/bash
# Script para executar migrações do Django no Cloud Run

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Executando migrações do Django${NC}"
echo ""

# Obter projeto
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    read -p "Digite o PROJECT_ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo "Projeto: $PROJECT_ID"
echo ""

# Verificar se job já existe
JOB_EXISTS=$(gcloud run jobs describe migrate-monpec --region=us-central1 2>/dev/null || echo "")

if [ -z "$JOB_EXISTS" ]; then
    echo -e "${YELLOW}Criando job de migração...${NC}"
    
    # Solicitar informações necessárias
    read -sp "SECRET_KEY do Django: " SECRET_KEY
    echo ""
    read -p "DB_NAME [monpec_db]: " DB_NAME
    DB_NAME=${DB_NAME:-monpec_db}
    read -p "DB_USER [monpec_user]: " DB_USER
    DB_USER=${DB_USER:-monpec_user}
    read -sp "DB_PASSWORD: " DB_PASSWORD
    echo ""
    read -p "CLOUD_SQL_CONNECTION_NAME (formato: PROJECT_ID:REGION:INSTANCE_NAME): " CLOUD_SQL_CONNECTION_NAME
    
    # Extrair instância do connection name
    INSTANCE_NAME=$(echo $CLOUD_SQL_CONNECTION_NAME | cut -d: -f3)
    
    echo ""
    echo -e "${YELLOW}Criando job...${NC}"
    
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
      --set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
      --set-env-vars="PYTHONUNBUFFERED=1" \
      --add-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
      --max-retries=3 \
      --task-timeout=600
    
    echo -e "${GREEN}Job criado!${NC}"
else
    echo -e "${GREEN}Job já existe.${NC}"
fi

echo ""
echo -e "${YELLOW}Executando migrações...${NC}"
gcloud run jobs execute migrate-monpec --region=us-central1 --wait

echo ""
echo -e "${GREEN}Migrações executadas com sucesso!${NC}"

