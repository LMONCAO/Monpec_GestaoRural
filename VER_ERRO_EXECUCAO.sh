#!/bin/bash
# Ver erro detalhado da última execução

JOB_NAME="migrate-monpec"
REGION="us-central1"

echo "========================================"
echo "🔍 Erro Detalhado da Execução"
echo "========================================"
echo ""

# Pegar última execução
LAST_EXEC=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --limit 1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LAST_EXEC" ]; then
    echo "Última execução: $LAST_EXEC"
    echo ""
    echo "Status completo:"
    gcloud run jobs executions describe $LAST_EXEC --region $REGION 2>/dev/null
    echo ""
else
    echo "Nenhuma execução encontrada"
fi

echo "========================================"
echo "📋 Logs da Execução (últimas 30 linhas)"
echo "========================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME" --limit 30 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -40
echo ""

echo "========================================"
echo "💡 Verificar Variáveis"
echo "========================================"
echo ""
echo "Variáveis do job:"
gcloud run jobs describe $JOB_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null | tr ',' '\n' | grep -E "DB_|DJANGO"
echo ""

echo "Cloud SQL instances configuradas:"
gcloud run jobs describe $JOB_NAME --region $REGION --format="value(spec.template.metadata.annotations)" 2>/dev/null | grep -o "cloudsql-instances[^,]*" || echo "Nenhuma encontrada"
echo ""



