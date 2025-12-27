#!/bin/bash
# ========================================
# CORRIGIR E EXECUTAR MIGRAÇÕES NOVAMENTE
# ========================================

set -e

PROJECT_ID="monpec-sistema-rural"
JOB_NAME="migrate-monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec"

# Configurar projeto
gcloud config set project $PROJECT_ID

echo "========================================"
echo "  CORRIGINDO E EXECUTANDO MIGRAÇÕES"
echo "========================================"
echo ""

# Primeiro, ver o erro da última execução
echo "1. Verificando último erro..."
LATEST_EXECUTION=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LATEST_EXECUTION" ]; then
    echo "   Execução: $LATEST_EXECUTION"
    echo ""
    echo "   Status:"
    gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].message)" 2>/dev/null || echo "   (Verificando logs...)"
    echo ""
    
    echo "   Últimas linhas dos logs:"
    gcloud alpha run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=50 2>/dev/null || \
    gcloud beta run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=50 2>/dev/null || \
    echo "   (Logs não disponíveis via CLI - verifique no console)"
    echo ""
fi

echo "2. Verificando configuração do job atual..."
gcloud run jobs describe $JOB_NAME --region $REGION --project $PROJECT_ID --format="yaml(spec.template.spec)" | grep -A 5 "env\|cloudSql\|containers" | head -20
echo ""

echo "3. Recriando job com configuração otimizada..."
echo ""

# Deletar job atual
gcloud run jobs delete $JOB_NAME --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true
sleep 2

# Criar job com configuração melhorada
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

gcloud run jobs create $JOB_NAME \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --project $PROJECT_ID \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 1 \
    --task-timeout 900 \
    --memory=2Gi \
    --cpu=2 \
    --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --service-account=${PROJECT_ID}@appspot.gserviceaccount.com

echo "✅ Job recriado"
echo ""

echo "4. Executando migrações (aguarde 2-5 minutos)..."
echo ""

# Executar e mostrar output em tempo real
gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID --wait

echo ""
echo "5. Verificando resultado..."
sleep 5

LATEST_EXECUTION=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LATEST_EXECUTION" ]; then
    STATUS=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
    MESSAGE=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].message)" 2>/dev/null || echo "")
    
    if [ "$STATUS" = "True" ]; then
        echo ""
        echo "✅✅✅ MIGRAÇÕES EXECUTADAS COM SUCESSO!"
        echo ""
        echo "Seu sistema está pronto! Teste agora:"
        echo "  https://monpec-29862706245.us-central1.run.app"
        echo "  https://monpec-fzzfjppzva-uc.a.run.app"
    else
        echo ""
        echo "❌ Execução falhou novamente"
        echo "   Status: $STATUS"
        echo "   Mensagem: $MESSAGE"
        echo ""
        echo "Verificando logs detalhados..."
        echo ""
        gcloud alpha run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        gcloud beta run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        echo "   Execute: gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --project $PROJECT_ID --limit=100"
    fi
fi

echo ""
echo "========================================"
echo ""








