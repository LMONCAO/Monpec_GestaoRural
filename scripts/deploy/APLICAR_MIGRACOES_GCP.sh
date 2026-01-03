#!/bin/bash
# Script para aplicar migrações no Google Cloud Run

SERVICE_NAME="${CLOUD_RUN_SERVICE:-monpec}"
REGION="${CLOUD_RUN_REGION:-us-central1}"
PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

if [ -z "$PROJECT_ID" ]; then
    echo "ERRO: PROJECT_ID não definido!"
    exit 1
fi

echo "========================================"
echo "Aplicar Migrações - Google Cloud Run"
echo "========================================"
echo ""

# Obter variáveis de ambiente do serviço
echo "Obtendo variáveis de ambiente do serviço..."
ENV_VARS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" | tr ',' '\n' | grep -E '^(SECRET_KEY|DB_|CLOUD_SQL)' | awk -F'=' '{print $1"="$2}' | tr '\n' ',' | sed 's/,$//')

if [ -z "$ENV_VARS" ]; then
    # Tentar ler do .env_producao
    if [ -f ".env_producao" ]; then
        source <(grep -v '^#' .env_producao | grep -v '^$' | sed 's/^/export /')
        ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"
        [ -n "$SECRET_KEY" ] && ENV_VARS="$ENV_VARS,SECRET_KEY=$SECRET_KEY"
        [ -n "$DB_NAME" ] && ENV_VARS="$ENV_VARS,DB_NAME=$DB_NAME"
        [ -n "$DB_USER" ] && ENV_VARS="$ENV_VARS,DB_USER=$DB_USER"
        [ -n "$DB_PASSWORD" ] && ENV_VARS="$ENV_VARS,DB_PASSWORD=$DB_PASSWORD"
        [ -n "$DB_HOST" ] && ENV_VARS="$ENV_VARS,DB_HOST=$DB_HOST"
        [ -n "$CLOUD_SQL_CONNECTION_NAME" ] && ENV_VARS="$ENV_VARS,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME"
    else
        ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"
    fi
fi

echo "Aplicando migrações..."
echo ""

# Criar job de migração se não existir
gcloud run jobs describe migrate-monpec --region $REGION &>/dev/null || {
    echo "Criando job de migração..."
    gcloud run jobs create migrate-monpec \
        --image $IMAGE_NAME:latest \
        --region $REGION \
        --set-env-vars "$ENV_VARS" \
        --command python \
        --args manage.py,migrate,--noinput \
        --max-retries 3 \
        --task-timeout 600
}

# Executar job
echo "Executando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrações aplicadas com sucesso!"
else
    echo ""
    echo "❌ Erro ao aplicar migrações!"
    exit 1
fi
















