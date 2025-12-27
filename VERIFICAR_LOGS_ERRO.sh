#!/bin/bash
# Script para verificar logs completos do job de migração

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
JOB_NAME="migrate-monpec"

echo "▶ Obtendo execuções recentes do job..."
EXECUTIONS=$(gcloud run jobs executions list --job "$JOB_NAME" --region "$REGION" --limit 1 --format="value(name)")

if [ -z "$EXECUTIONS" ]; then
    echo "❌ Nenhuma execução encontrada"
    exit 1
fi

EXECUTION_NAME=$(echo $EXECUTIONS | awk '{print $NF}')
echo "✓ Execução encontrada: $EXECUTION_NAME"
echo ""

echo "▶ Obtendo logs completos..."
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME AND resource.labels.location=$REGION" \
    --limit 100 \
    --format json \
    --project "$PROJECT_ID" | \
    jq -r '.[] | "\(.timestamp) [\(.severity)] \(.textPayload // .jsonPayload.message // "")"' | \
    tail -50

echo ""
echo "▶ Para ver logs detalhados de uma execução específica:"
echo "   gcloud run jobs executions describe $EXECUTION_NAME --region=$REGION"
echo ""




