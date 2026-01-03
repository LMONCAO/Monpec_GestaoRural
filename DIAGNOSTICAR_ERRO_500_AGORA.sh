#!/bin/bash
# Diagnosticar erro 500 atual
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔍 Diagnosticando erro 500 - Logs mais recentes"
echo "============================================================"
echo ""

echo "📋 Últimos 10 erros:"
echo ""
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
  --limit=10 \
  --format="value(timestamp,textPayload)" \
  --freshness=10m | head -30

echo ""
echo "============================================================"
echo "📋 Stack trace completo do último erro:"
echo "============================================================"
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
  --limit=50 \
  --format="value(textPayload)" \
  --freshness=10m | grep -A 30 "Traceback\|ProgrammingError\|DoesNotExist\|Exception" | head -50

