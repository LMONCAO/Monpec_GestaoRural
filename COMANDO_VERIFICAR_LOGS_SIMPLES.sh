#!/bin/bash
# Script simples para verificar logs do Cloud Run

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"

echo "🔍 Buscando logs mais recentes do serviço $SERVICE_NAME..."
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "✅ Logs exibidos acima"
echo ""
echo "Para ver logs em tempo real:"
echo "gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --project=$PROJECT_ID"

