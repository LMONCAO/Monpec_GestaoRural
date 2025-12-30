#!/bin/bash
# ========================================
# CORRIGIR MIGRAÇÕES QUE FALHARAM
# ========================================

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
JOB_NAME="migrate-monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================"
echo "  CORRIGINDO MIGRAÇÕES"
echo "========================================"
echo ""

# 1. Verificar status do job
echo "1. Verificando status do job..."
gcloud run jobs describe $JOB_NAME --region $REGION 2>&1 || echo "Job não existe ainda"
echo ""

# 2. Deletar job antigo se existir
echo "2. Removendo job antigo (se existir)..."
gcloud run jobs delete $JOB_NAME --region $REGION --quiet 2>&1 | grep -v "not found" || true
echo "✅ Job antigo removido"
echo ""

# 3. Criar job novamente com configuração corrigida
echo "3. Criando job de migração corrigido..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

gcloud run jobs create $JOB_NAME \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600 \
    --memory=2Gi \
    --cpu=2 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --service-account=${PROJECT_ID}@appspot.gserviceaccount.com 2>&1

echo "✅ Job criado"
echo ""

# 4. Executar migrações
echo "4. Executando migrações..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait
echo ""

# 5. Verificar resultado
echo "5. Verificando resultado..."
EXECUTION_STATUS=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --limit=1 --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")

if [ "$EXECUTION_STATUS" = "True" ]; then
    echo "✅ Migrações executadas com sucesso!"
else
    echo "⚠️  Status: $EXECUTION_STATUS"
    echo ""
    echo "Verificando logs..."
    gcloud run jobs executions list --job $JOB_NAME --region $REGION --limit=1 --format="value(name)" | head -1 | xargs -I {} gcloud run jobs executions logs read {} --region $REGION --limit=50
fi

echo ""
echo "========================================"
echo "  CONCLUSÃO"
echo "========================================"
echo ""
echo "Se as migrações foram bem-sucedidas, teste o sistema:"
echo "  https://monpec-29862706245.us-central1.run.app"
echo ""
















