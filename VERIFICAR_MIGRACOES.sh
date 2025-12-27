#!/bin/bash
# ========================================
# VERIFICAR STATUS DAS MIGRAÇÕES
# ========================================

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
JOB_NAME="migrate-monpec"

echo "========================================"
echo "  VERIFICANDO STATUS DAS MIGRAÇÕES"
echo "========================================"
echo ""

gcloud config set project $PROJECT_ID > /dev/null 2>&1

# Obter a última execução
echo "1. Buscando última execução do job..."
LATEST_EXECUTION=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -z "$LATEST_EXECUTION" ]; then
    echo "❌ Nenhuma execução encontrada!"
    exit 1
fi

echo "✅ Execução encontrada: $LATEST_EXECUTION"
echo ""

# Verificar status
echo "2. Verificando status da execução..."
STATUS=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].status)" 2>/dev/null)
COMPLETED_COUNT=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.succeededCount)" 2>/dev/null)
FAILED_COUNT=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.failedCount)" 2>/dev/null)

echo "   Status: $STATUS"
echo "   Tarefas concluídas: ${COMPLETED_COUNT:-0}"
echo "   Tarefas falhadas: ${FAILED_COUNT:-0}"
echo ""

if [ "$STATUS" = "True" ] && [ "${COMPLETED_COUNT:-0}" -gt 0 ]; then
    echo "✅✅✅ SUCESSO! MIGRAÇÕES EXECUTADAS COM SUCESSO!"
    echo ""
    echo "🌐 Seu sistema está pronto:"
    echo "   https://monpec-29862706245.us-central1.run.app"
    echo ""
    exit 0
elif [ "$STATUS" = "False" ] || [ "${FAILED_COUNT:-0}" -gt 0 ]; then
    echo "❌ ERRO NA EXECUÇÃO!"
    echo ""
    echo "3. Buscando logs do erro..."
    echo "========================================"
    echo ""
    
    # Tentar obter logs da execução
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME AND resource.labels.location=$REGION AND resource.labels.execution_name=$LATEST_EXECUTION" \
        --project $PROJECT_ID \
        --limit=100 \
        --format="table(timestamp,severity,textPayload)" \
        --freshness=1h 2>/dev/null | head -50
    
    echo ""
    echo "========================================"
    echo ""
    echo "💡 Para ver mais detalhes:"
    echo "   gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION"
    echo ""
    echo "💡 Para ver logs completos:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --limit=200 --format=\"table(timestamp,severity,textPayload)\""
    echo ""
    exit 1
else
    echo "⏳ Execução ainda em andamento..."
    echo ""
    echo "💡 Para acompanhar em tempo real:"
    echo "   gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --watch"
    echo ""
    exit 0
fi








