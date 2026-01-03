#!/bin/bash
# Verificar erro atual completo

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔍 VERIFICANDO ERRO ATUAL"
echo "=========================================="

gcloud config set project $PROJECT_ID

echo ""
echo "Último erro completo:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=1 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "Últimos 5 erros (resumo):"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | grep -E "ModuleNotFoundError|ImportError|IndentationError|SyntaxError|File.*line" | head -20

echo ""
echo "Status do serviço:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.conditions)" --project=$PROJECT_ID




