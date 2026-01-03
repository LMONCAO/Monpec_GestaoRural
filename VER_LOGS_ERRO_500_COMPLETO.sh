#!/bin/bash
# Ver logs completos do erro 500
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔍 Verificando logs completos do erro 500..."
echo "============================================================"
echo ""

echo "📋 Últimos 50 logs de ERRO:"
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
  --limit=50 \
  --format="value(timestamp,severity,textPayload,jsonPayload.message)" \
  --freshness=15m | head -50

echo ""
echo "============================================================"
echo "📋 Stack trace completo (últimos erros):"
echo "============================================================"
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND (textPayload=~'Traceback' OR textPayload=~'Error' OR textPayload=~'Exception')" \
  --limit=100 \
  --format="value(textPayload)" \
  --freshness=15m | grep -A 30 "Traceback\|Error\|Exception" | head -100

echo ""
echo "============================================================"
echo "📋 Logs recentes do serviço (últimas 30 linhas):"
echo "============================================================"
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" \
  --limit=30 \
  --format="value(timestamp,textPayload)" \
  --freshness=15m | tail -30

