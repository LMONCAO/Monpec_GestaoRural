#!/bin/bash
# Verificar se ainda há migrations pendentes e fazer deploy
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 Verificando logs da última revisão"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND resource.labels.revision_name=monpec-00013-znt" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20

echo ""
echo "============================================================"
echo "📊 Verificando estado das migrations"
echo "============================================================"
echo ""

gcloud run jobs delete verificar-migrations-final --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create verificar-migrations-final \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,showmigrations,--list" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute verificar-migrations-final --region=$REGION --wait

echo ""
echo "📋 Estado das migrations:"
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-migrations-final" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[X\]|\[ \]|gestao_rural|sessions" | tail -30

gcloud run jobs delete verificar-migrations-final --region=$REGION --quiet 2>/dev/null || true


