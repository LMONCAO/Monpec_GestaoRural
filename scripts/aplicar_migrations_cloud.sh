#!/bin/bash
# Script para Aplicar Migrations no Cloud SQL
# Uso: ./scripts/aplicar_migrations_cloud.sh

set -e

echo "📦 Aplicando migrations no Cloud SQL..."

# Variáveis
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"seu-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="monpec"
INSTANCE_NAME=${CLOUD_SQL_INSTANCE:-"monpec-db"}

# Verificar se job existe
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
        --max-retries 1
else
    echo "Atualizando job de migrations..."
    gcloud run jobs update migrate-db \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --region $REGION \
        --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp \
        --add-cloudsql-instances $PROJECT_ID:$REGION:$INSTANCE_NAME \
        --command python \
        --args manage.py,migrate \
        --memory 512Mi \
        --timeout 600
fi

# Executar migrations
echo "Executando migrations..."
gcloud run jobs execute migrate-db --region=$REGION --wait

echo "✅ Migrations aplicadas com sucesso!"

