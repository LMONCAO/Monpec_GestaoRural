#!/bin/bash
# ========================================
# VER ERRO REAL DA EXECUÇÃO
# ========================================

PROJECT_ID="monpec-sistema-rural"
JOB_NAME="migrate-monpec"
REGION="us-central1"
EXECUTION_NAME="migrate-monpec-gbrqh"

echo "========================================"
echo "  DIAGNOSTICANDO ERRO DA EXECUÇÃO"
echo "========================================"
echo ""

# Configurar projeto
gcloud config set project $PROJECT_ID > /dev/null 2>&1

echo "1. Verificando status da execução..."
gcloud run jobs executions describe $EXECUTION_NAME --region $REGION --project $PROJECT_ID --format="yaml(status)" | head -50
echo ""

echo "2. Verificando logs da execução..."
echo "   (Tentando alpha primeiro, depois beta, depois estável)"
echo ""

# Tentar alpha
gcloud alpha run jobs executions logs read $EXECUTION_NAME --region $REGION --project $PROJECT_ID --limit=200 2>/dev/null && exit 0

# Tentar beta
gcloud beta run jobs executions logs read $EXECUTION_NAME --region $REGION --project $PROJECT_ID --limit=200 2>/dev/null && exit 0

# Se não funcionou, tentar via Cloud Logging
echo "3. Buscando logs via Cloud Logging..."
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME AND resource.labels.location=$REGION" \
    --project $PROJECT_ID \
    --limit=50 \
    --format="table(timestamp,severity,textPayload,jsonPayload.message)" \
    --freshness=1h

echo ""
echo "========================================"
echo ""
echo "Se não apareceram logs acima, tente:"
echo "  gcloud logging read \"resource.type=cloud_run_job\" --project $PROJECT_ID --limit=100"
echo ""
