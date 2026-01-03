#!/bin/bash
# ========================================
# COMANDO ÚNICO CORRIGIDO - EXECUTAR AGORA
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

# Deletar job antigo
echo "1. Removendo job antigo..."
gcloud run jobs delete $JOB_NAME --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true
echo "✅ Removido"
echo ""

# Criar job corrigido
echo "2. Criando job corrigido..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

gcloud run jobs create $JOB_NAME \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --project $PROJECT_ID \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600 \
    --memory=2Gi \
    --cpu=2 \
    --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

echo "✅ Job criado"
echo ""

# Executar migrações
echo "3. Executando migrações (pode levar 2-3 minutos)..."
gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID --wait

echo ""
echo "========================================"
echo "✅✅✅ CONCLUÍDO!"
echo "========================================"
echo ""
echo "Teste seu sistema:"
echo "  https://monpec-29862706245.us-central1.run.app"
echo "  https://monpec-fzzfjppzva-uc.a.run.app"
echo ""















