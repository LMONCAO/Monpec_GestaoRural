#!/bin/bash
# Script para configurar variáveis de ambiente no Google Cloud Run

# Configurações
SERVICE_NAME="${CLOUD_RUN_SERVICE:-monpec}"
REGION="${CLOUD_RUN_REGION:-us-central1}"
PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"

if [ -z "$PROJECT_ID" ]; then
    echo "ERRO: PROJECT_ID não definido!"
    echo "Defina com: export GCP_PROJECT=seu-projeto-id"
    exit 1
fi

echo "========================================"
echo "Configurar Variáveis de Ambiente - GCP"
echo "========================================"
echo ""
echo "Serviço: $SERVICE_NAME"
echo "Região: $REGION"
echo "Projeto: $PROJECT_ID"
echo ""

# Ler variáveis do arquivo .env_producao se existir
if [ -f ".env_producao" ]; then
    echo "Lendo variáveis de .env_producao..."
    source <(grep -v '^#' .env_producao | grep -v '^$' | sed 's/^/export /')
fi

# Montar string de variáveis de ambiente
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

# Adicionar SECRET_KEY
if [ -n "$SECRET_KEY" ]; then
    ENV_VARS="$ENV_VARS,SECRET_KEY=$SECRET_KEY"
    echo "✓ SECRET_KEY configurada"
else
    echo "⚠ SECRET_KEY não encontrada!"
    read -p "Digite a SECRET_KEY: " SECRET_KEY
    ENV_VARS="$ENV_VARS,SECRET_KEY=$SECRET_KEY"
fi

# Adicionar configurações do Mercado Pago
if [ -n "$MERCADOPAGO_ACCESS_TOKEN" ]; then
    ENV_VARS="$ENV_VARS,MERCADOPAGO_ACCESS_TOKEN=$MERCADOPAGO_ACCESS_TOKEN"
    echo "✓ MERCADOPAGO_ACCESS_TOKEN configurada"
else
    echo "⚠ MERCADOPAGO_ACCESS_TOKEN não encontrada!"
    read -p "Digite o MERCADOPAGO_ACCESS_TOKEN: " MERCADOPAGO_ACCESS_TOKEN
    ENV_VARS="$ENV_VARS,MERCADOPAGO_ACCESS_TOKEN=$MERCADOPAGO_ACCESS_TOKEN"
fi

if [ -n "$MERCADOPAGO_PUBLIC_KEY" ]; then
    ENV_VARS="$ENV_VARS,MERCADOPAGO_PUBLIC_KEY=$MERCADOPAGO_PUBLIC_KEY"
    echo "✓ MERCADOPAGO_PUBLIC_KEY configurada"
fi

# Adicionar outras configurações do Mercado Pago
ENV_VARS="$ENV_VARS,PAYMENT_GATEWAY_DEFAULT=mercadopago"
ENV_VARS="$ENV_VARS,MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/"
ENV_VARS="$ENV_VARS,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/"
echo "✓ Configurações do Mercado Pago adicionadas"

# Adicionar configurações de banco de dados
if [ -n "$DB_NAME" ]; then
    ENV_VARS="$ENV_VARS,DB_NAME=$DB_NAME"
    echo "✓ DB_NAME: $DB_NAME"
fi

if [ -n "$DB_USER" ]; then
    ENV_VARS="$ENV_VARS,DB_USER=$DB_USER"
    echo "✓ DB_USER: $DB_USER"
fi

if [ -n "$DB_PASSWORD" ]; then
    ENV_VARS="$ENV_VARS,DB_PASSWORD=$DB_PASSWORD"
    echo "✓ DB_PASSWORD: configurada"
fi

if [ -n "$DB_HOST" ]; then
    ENV_VARS="$ENV_VARS,DB_HOST=$DB_HOST"
    echo "✓ DB_HOST: $DB_HOST"
fi

if [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
    ENV_VARS="$ENV_VARS,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME"
    echo "✓ CLOUD_SQL_CONNECTION_NAME: $CLOUD_SQL_CONNECTION_NAME"
fi

echo ""
echo "Atualizando variáveis de ambiente no Cloud Run..."
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars "$ENV_VARS"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Variáveis de ambiente atualizadas com sucesso!"
else
    echo ""
    echo "❌ Erro ao atualizar variáveis de ambiente!"
    exit 1
fi








