#!/bin/bash
# Script para ver logs detalhados do erro 500
# Execute no Google Cloud Shell

echo "============================================================"
echo "📋 LOGS DETALHADOS - ERRO 500"
echo "============================================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"

gcloud config set project $PROJECT_ID

echo "1️⃣ Últimos 20 erros do serviço:"
echo ""
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=20 --format="table(timestamp,severity,textPayload)"

echo ""
echo "============================================================"
echo "2️⃣ Últimos 30 logs gerais (incluindo INFO e WARNING):"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=30 --format="table(timestamp,severity,textPayload)"

echo ""
echo "============================================================"
echo "3️⃣ Logs do job corrigir-500 (se existir):"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=20 --format="table(timestamp,severity,textPayload)" 2>/dev/null || echo "   Nenhum log encontrado para o job"

echo ""
echo "============================================================"
echo "✅ Logs exibidos acima"
echo "============================================================"
echo ""
echo "💡 Para ver logs em tempo real:"
echo "   gcloud logging tail \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\""
echo ""
