#!/bin/bash
# Script para executar migrações e criar admin usando Cloud Run Jobs
# Este script cria/atualiza um job do Cloud Run para executar migrações e criar admin

set -e

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
DJANGO_SUPERUSER_PASSWORD="L6171r12@@"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec:latest"

echo "=========================================="
echo "CRIAR JOB PARA MIGRAÇÕES E ADMIN"
echo "=========================================="
echo ""

# Criar ou atualizar o job
echo "🔨 Criando/atualizando Cloud Run Job..."
gcloud run jobs create migrate-and-create-admin \
    --image=$IMAGE_NAME \
    --region=$REGION \
    --platform=managed \
    --add-cloudsql-instances=${PROJECT_ID}:${REGION}:${DB_INSTANCE} \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=${SECRET_KEY},CLOUD_SQL_CONNECTION_NAME=${PROJECT_ID}:${REGION}:${DB_INSTANCE},DB_NAME=${DB_NAME},DB_USER=${DB_USER},DB_PASSWORD=${DB_PASSWORD},DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD},GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=1800 \
    --task-timeout=1800 \
    --max-retries=1 \
    --command="sh" \
    --args="-c,python manage.py migrate --noinput && python manage.py garantir_admin --senha \${DJANGO_SUPERUSER_PASSWORD} && echo '✅ Migrações e admin criado com sucesso!'" \
    --quiet 2>/dev/null || \
gcloud run jobs update migrate-and-create-admin \
    --image=$IMAGE_NAME \
    --region=$REGION \
    --platform=managed \
    --add-cloudsql-instances=${PROJECT_ID}:${REGION}:${DB_INSTANCE} \
    --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=${SECRET_KEY},CLOUD_SQL_CONNECTION_NAME=${PROJECT_ID}:${REGION}:${DB_INSTANCE},DB_NAME=${DB_NAME},DB_USER=${DB_USER},DB_PASSWORD=${DB_PASSWORD},DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD},GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=1800 \
    --task-timeout=1800 \
    --max-retries=1 \
    --command="sh" \
    --args="-c,python manage.py migrate --noinput && python manage.py garantir_admin --senha \${DJANGO_SUPERUSER_PASSWORD} && echo '✅ Migrações e admin criado com sucesso!'" \
    --quiet

echo ""
echo "✅ Job criado/atualizado com sucesso!"
echo ""

# Executar o job
echo "🚀 Executando job..."
gcloud run jobs execute migrate-and-create-admin \
    --region=$REGION \
    --wait

echo ""
echo "✅ Processo concluído!"
echo ""
echo "Verificando logs do job..."
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-and-create-admin" --limit=50 --format=json

