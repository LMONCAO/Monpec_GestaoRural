#!/bin/bash
# Ver logs do erro 500 atual após criar tabela
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
gcloud config set project $PROJECT_ID

echo "🔍 Verificando logs do erro 500 mais recente..."
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
  --limit=20 \
  --format="value(timestamp,severity,textPayload)" \
  --freshness=5m | head -30

echo ""
echo "============================================================"
echo "📋 Stack trace completo:"
echo "============================================================"
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
  --limit=50 \
  --format="value(textPayload)" \
  --freshness=5m | grep -A 25 "Traceback\|Error\|Exception" | head -50


