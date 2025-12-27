#!/bin/bash
# ========================================
# TESTAR MIGRAÇÕES COM DEBUG DETALHADO
# ========================================

PROJECT_ID="monpec-sistema-rural"
JOB_NAME="migrate-monpec-debug"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec"

gcloud config set project $PROJECT_ID

echo "========================================"
echo "  TESTANDO MIGRAÇÕES COM DEBUG"
echo "========================================"
echo ""

# Criar job de teste com mais verbosidade
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=True,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

echo "1. Criando job de teste..."
gcloud run jobs delete $JOB_NAME --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true

gcloud run jobs create $JOB_NAME \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --project $PROJECT_ID \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput,--verbosity=3 \
    --max-retries 1 \
    --task-timeout 900 \
    --memory=2Gi \
    --cpu=2 \
    --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

echo "✅ Job criado"
echo ""

echo "2. Executando com verbosidade máxima..."
gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID --wait

echo ""
echo "3. Verificando logs..."
sleep 3
LATEST_EXECUTION=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LATEST_EXECUTION" ]; then
    echo "   Logs da execução:"
    gcloud alpha run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=200 2>/dev/null || \
    gcloud beta run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=200 2>/dev/null || \
    echo "   (Execute no console para ver logs completos)"
fi

echo ""
echo "========================================"
echo ""








