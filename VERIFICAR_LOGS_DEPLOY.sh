#!/bin/bash
# Script para verificar logs do Cloud Run

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"

echo "=========================================="
echo "  VERIFICANDO LOGS DO CLOUD RUN"
echo "=========================================="
echo ""

echo "📋 Últimos 50 logs do serviço $SERVICE_NAME:"
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "=========================================="
echo "  LOGS COMPLETOS (últimas 100 linhas)"
echo "=========================================="
echo ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=100 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | tail -100

echo ""
echo "=========================================="
echo "  URL PARA VER LOGS NO NAVEGADOR"
echo "=========================================="
echo ""
echo "https://console.cloud.google.com/logs/viewer?project=$PROJECT_ID&resource=cloud_run_revision/service_name/$SERVICE_NAME"
echo ""

