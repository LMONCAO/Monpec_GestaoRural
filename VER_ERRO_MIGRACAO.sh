#!/bin/bash
# Script para ver detalhes do erro da migração

JOB_NAME="migrate-monpec"
REGION="us-central1"

echo "========================================"
echo "🔍 Detalhes do Erro da Migração"
echo "========================================"
echo ""

# Última execução
LAST_EXEC=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --limit 1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LAST_EXEC" ]; then
    echo "Última execução: $LAST_EXEC"
    echo ""
    echo "Status detalhado:"
    gcloud run jobs executions describe $LAST_EXEC --region $REGION 2>/dev/null
    echo ""
else
    echo "Nenhuma execução encontrada"
fi

echo "========================================"
echo "📋 Logs da Execução"
echo "========================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME" --limit 30 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -40
echo ""



