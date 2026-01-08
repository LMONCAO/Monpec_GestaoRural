#!/bin/bash
# Verificar logs do erro 500 atual
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔍 Verificando logs do erro 500..."
echo "============================================================"
echo ""

echo "📋 Últimos logs do serviço monpec:"
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)" \
  --freshness=10m

echo ""
echo "============================================================"
echo "📋 Logs completos (últimas 30 linhas):"
echo "============================================================"
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
  --limit=30 \
  --format="value(textPayload)" \
  --freshness=10m | tail -30


