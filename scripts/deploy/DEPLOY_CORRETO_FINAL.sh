#!/bin/bash
# Script limpo para rebuild e deploy - SEM comentários inline que quebram o comando

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
JOB_NAME="migrate-monpec"

echo ""
echo "========================================"
echo "  DEPLOY CORRETO - SISTEMA MONPEC"
echo "========================================"
echo ""

echo "Passo 1: Reconstruindo a imagem Docker..."
gcloud builds submit --tag "${IMAGE_NAME}:latest" --timeout=20m
echo "✓ Build concluído"
echo ""

echo "Passo 2: Atualizando o job de migração..."
gcloud run jobs update "${JOB_NAME}" \
  --image "${IMAGE_NAME}:latest" \
  --region "${REGION}" \
  --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1' \
  --set-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" \
  --memory 2Gi \
  --cpu 1 \
  --max-retries 3 \
  --task-timeout 600 \
  --command python \
  --args "manage.py,migrate,--noinput" \
  --quiet
echo "✓ Job atualizado"
echo ""

echo "Passo 3: Executando migração..."
gcloud run jobs execute "${JOB_NAME}" --region "${REGION}" --wait
echo "✓ Migração concluída"
echo ""

echo "========================================"
echo "✓ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo ""











