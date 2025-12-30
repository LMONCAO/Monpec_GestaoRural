#!/bin/bash
# Verificar erro atual do serviço

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔍 VERIFICANDO ERRO ATUAL"
echo "=========================================="

gcloud config set project $PROJECT_ID

echo ""
echo "Últimos 3 erros:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=3 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | head -150

echo ""
echo "Últimos logs gerais:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=10 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | tail -50





