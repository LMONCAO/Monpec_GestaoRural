#!/bin/bash
# Script para aplicar migrações no Cloud Run

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/monpec:latest"

echo "========================================"
echo "Aplicando migrações do Django"
echo "========================================"
echo ""

# Criar job para migrações
echo "Criando job de migração..."
gcloud run jobs create migrate-monpec \
    --image $IMAGE \
    --region $REGION \
    --command python \
    --args "manage.py,migrate" \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
    --max-retries 3 \
    --task-timeout 600

echo ""
echo "Executando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait

echo ""
echo "========================================"
echo "Migrações aplicadas com sucesso!"
echo "========================================"
echo ""


