#!/bin/bash
# Execute este comando DIRETO no Cloud Shell (copie e cole)

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔍 VERIFICANDO LOGS DO ERRO 500"
echo "=========================================="
echo ""

gcloud config set project $PROJECT_ID

echo "Últimos 5 erros:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | head -100

echo ""
echo "Últimos logs gerais:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=10 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | tail -50





