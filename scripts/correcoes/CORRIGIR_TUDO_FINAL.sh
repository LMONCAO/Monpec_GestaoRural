#!/bin/bash
# ========================================
# CORRIGIR TUDO - CONEXÃO COM BANCO
# ========================================

set -e

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec"
JOB_NAME="migrate-monpec"
CLOUD_SQL_INSTANCE="monpec-sistema-rural:us-central1:monpec-db"

gcloud config set project $PROJECT_ID

echo "========================================"
echo "  CORRIGINDO CONEXÃO COM BANCO"
echo "========================================"
echo ""

echo "1. Verificando instância Cloud SQL..."
if gcloud sql instances describe monpec-db --project $PROJECT_ID > /dev/null 2>&1; then
    echo "✅ Instância Cloud SQL encontrada"
else
    echo "❌ Instância Cloud SQL NÃO encontrada!"
    echo "   Execute: gcloud sql instances list"
    exit 1
fi
echo ""

echo "2. Garantindo permissões do Cloud Run para Cloud SQL..."
SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"
echo "   Service Account: $SERVICE_ACCOUNT"
echo "   Concedendo permissão Cloud SQL Client..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudsql.client" \
    --quiet 2>&1 | grep -v "Updated IAM policy" || echo "   Permissão já configurada"
echo "✅ Permissões verificadas"
echo ""

echo "3. Removendo job antigo..."
gcloud run jobs delete $JOB_NAME --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true
echo "✅ Removido"
echo ""

echo "4. Criando job com configuração corrigida..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_INSTANCE,PYTHONUNBUFFERED=1"

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
    --set-cloudsql-instances=$CLOUD_SQL_INSTANCE \
    --service-account=$SERVICE_ACCOUNT

echo "✅ Job criado"
echo ""

echo "5. Executando migrações..."
gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID --wait

echo ""
echo "6. Verificando resultado..."
sleep 5

LATEST_EXECUTION=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LATEST_EXECUTION" ]; then
    STATUS=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
    
    if [ "$STATUS" = "True" ]; then
        echo ""
        echo "✅✅✅ SUCESSO! MIGRAÇÕES EXECUTADAS!"
        echo ""
        echo "Seu sistema está pronto:"
        echo "  https://monpec-29862706245.us-central1.run.app"
        echo "  https://monpec-fzzfjppzva-uc.a.run.app"
    else
        echo ""
        echo "⚠️  Status: $STATUS"
        echo ""
        echo "Verificando logs..."
        gcloud alpha run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        gcloud beta run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        echo "   Ver logs: https://console.cloud.google.com/run/jobs/executions/details/us-central1/$LATEST_EXECUTION?project=$PROJECT_ID"
    fi
fi

echo ""
echo "========================================"
echo ""















