#!/bin/bash
# COMANDO SIMPLES PARA CORRIGIR ERRO 500
# Copie TODO este conteúdo e cole no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

echo "🔍 Primeiro, vamos ver os logs de erro..."
echo ""
gcloud config set project $PROJECT_ID
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=5 --format="value(textPayload)" 2>/dev/null | head -3

echo ""
echo "🔧 Aplicando migrations..."
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=600

echo "⏱️  Executando (aguarde 2-4 minutos)..."
gcloud run jobs execute corrigir-500 --region=$REGION --wait

echo ""
echo "🧹 Limpando..."
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "🔄 Reiniciando serviço..."
gcloud run services update $SERVICE_NAME --region=$REGION --update-env-vars="RESTART=$(date +%s)" --quiet

echo ""
echo "✅ Concluído! Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
