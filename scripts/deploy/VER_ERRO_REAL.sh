#!/bin/bash
# ========================================
# VER ERRO REAL DA EXECUÇÃO
# ========================================

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
EXECUTION_NAME="migrate-monpec-vzccq"

echo "========================================"
echo "  DIAGNOSTICANDO ERRO REAL"
echo "========================================"
echo ""

gcloud config set project $PROJECT_ID > /dev/null 2>&1

echo "1. Verificando logs da execução..."
echo ""

gcloud alpha run jobs executions logs read $EXECUTION_NAME --region $REGION --project $PROJECT_ID --limit=200 2>/dev/null || \
gcloud beta run jobs executions logs read $EXECUTION_NAME --region $REGION --project $PROJECT_ID --limit=200 2>/dev/null || \
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-monpec AND resource.labels.location=$REGION" --project $PROJECT_ID --limit=50 --format="table(timestamp,severity,textPayload)" --freshness=1h

echo ""
echo "========================================"
echo ""
