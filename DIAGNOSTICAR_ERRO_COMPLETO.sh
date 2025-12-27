#!/bin/bash
# Script completo para diagnosticar o erro do job de migração

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
JOB_NAME="migrate-monpec"

echo "========================================"
echo "  DIAGNÓSTICO DO ERRO DE MIGRAÇÃO"
echo "========================================"
echo ""

echo "▶ 1. Verificando última execução do job..."
EXECUTIONS=$(gcloud run jobs executions list --job "$JOB_NAME" --region "$REGION" --limit 1 --format="value(name)")
if [ -z "$EXECUTIONS" ]; then
    echo "❌ Nenhuma execução encontrada"
    exit 1
fi
EXECUTION_NAME=$(echo $EXECUTIONS | awk '{print $NF}')
echo "✓ Execução: $EXECUTION_NAME"
echo ""

echo "▶ 2. Obtendo detalhes da execução..."
gcloud run jobs executions describe "$EXECUTION_NAME" --region "$REGION" --format="yaml(status)"
echo ""

echo "▶ 3. Verificando configuração do job (variáveis de ambiente e Cloud SQL)..."
gcloud run jobs describe "$JOB_NAME" --region "$REGION" --format="yaml(spec.template.spec)" | grep -A 20 "containers:"
echo ""

echo "▶ 4. Obtendo logs completos (últimos 100)..."
echo "--- INÍCIO DOS LOGS ---"
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME AND resource.labels.location=$REGION" \
    --limit 100 \
    --format="table(timestamp,severity,textPayload)" \
    --project "$PROJECT_ID" | head -50
echo "--- FIM DOS LOGS ---"
echo ""

echo "▶ 5. Verificando apenas erros críticos..."
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME AND severity>=ERROR" \
    --limit 20 \
    --format="table(timestamp,severity,textPayload)" \
    --project "$PROJECT_ID"
echo ""

echo "========================================"
echo "  PRÓXIMOS PASSOS"
echo "========================================"
echo ""
echo "1. Verifique se o erro ainda é sobre 'openpyxl' ou se mudou"
echo "2. Verifique se as variáveis de ambiente estão corretas"
echo "3. Verifique se a conexão Cloud SQL está configurada corretamente"
echo ""
echo "Para ver logs detalhados em tempo real:"
echo "  gcloud logging tail \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --project $PROJECT_ID"
echo ""




