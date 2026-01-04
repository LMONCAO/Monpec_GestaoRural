#!/bin/bash
# Comando simples para rebuild (use se não tiver cloudbuild-config.yaml no Cloud Shell)
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${TIMESTAMP}"

gcloud config set project $PROJECT_ID

echo "🔨 Buildando imagem..."
gcloud builds submit --tag $IMAGE_NAME --timeout=600s

echo ""
echo "🚀 Fazendo deploy..."
gcloud run deploy $SERVICE_NAME \
  --region=$REGION \
  --image=$IMAGE_NAME \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --allow-unauthenticated \
  --quiet

echo ""
echo "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/"


