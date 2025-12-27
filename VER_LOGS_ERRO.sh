#!/bin/bash
# Script para ver os logs detalhados do erro da migração

JOB_NAME="migrate-monpec"
REGION="us-central1"

echo "========================================"
echo "🔍 Logs Detalhados do Erro"
echo "========================================"
echo ""

# Última execução
LAST_EXEC=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --limit 1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LAST_EXEC" ]; then
    echo "Última execução: $LAST_EXEC"
    echo ""
    echo "Status completo:"
    gcloud run jobs executions describe $LAST_EXEC --region $REGION 2>/dev/null
    echo ""
fi

echo "========================================"
echo "📋 Logs do Job (últimas 50 linhas)"
echo "========================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME" --limit 50 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -60
echo ""

echo "========================================"
echo "💡 Próximos Passos"
echo "========================================"
echo ""
echo "Se o erro for relacionado a variáveis de ambiente, execute:"
echo "  SERVICE_ENV=\$(gcloud run services describe monpec --region us-central1 --format=\"value(spec.template.spec.containers[0].env)\")"
echo "  gcloud run jobs update migrate-monpec --region us-central1 --update-env-vars \"\$SERVICE_ENV\""
echo ""
echo "Se o erro for de conexão com banco, verifique:"
echo "  - DB_HOST está correto?"
echo "  - DB_USER e DB_PASSWORD estão corretos?"
echo "  - O Cloud SQL está acessível?"
echo ""





















