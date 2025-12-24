#!/bin/bash
# Script para configurar variáveis de ambiente no Cloud Run

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Configurando variáveis de ambiente no Cloud Run${NC}"
echo ""

# Obter projeto
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    read -p "Digite o PROJECT_ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo "Projeto: $PROJECT_ID"
echo ""

# Solicitar valores
read -sp "SECRET_KEY do Django: " SECRET_KEY
echo ""
read -p "DB_NAME [monpec_db]: " DB_NAME
DB_NAME=${DB_NAME:-monpec_db}
read -p "DB_USER [monpec_user]: " DB_USER
DB_USER=${DB_USER:-monpec_user}
read -sp "DB_PASSWORD: " DB_PASSWORD
echo ""
read -p "CLOUD_SQL_CONNECTION_NAME (formato: PROJECT_ID:REGION:INSTANCE_NAME): " CLOUD_SQL_CONNECTION_NAME
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
  --set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-env-vars="MERCADOPAGO_ACCESS_TOKEN=$MERCADOPAGO_ACCESS_TOKEN" \
  --set-env-vars="MERCADOPAGO_PUBLIC_KEY=$MERCADOPAGO_PUBLIC_KEY" \
  --set-env-vars="MERCADOPAGO_SUCCESS_URL=$SITE_URL/assinaturas/sucesso/" \
  --set-env-vars="MERCADOPAGO_CANCEL_URL=$SITE_URL/assinaturas/cancelado/" \
  --set-env-vars="SITE_URL=$SITE_URL" \
  --set-env-vars="PAYMENT_GATEWAY_DEFAULT=mercadopago" \
  --set-env-vars="PYTHONUNBUFFERED=1"

echo ""
echo -e "${GREEN}Variáveis configuradas com sucesso!${NC}"


