#!/bin/bash
# Script rápido para deploy sem --no-cache

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "🔨 Fazendo build..."
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
LATEST_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

gcloud builds submit --tag $IMAGE_TAG

echo "✅ Build concluído. Marcando como latest..."
gcloud container images add-tag $IMAGE_TAG $LATEST_TAG --quiet

echo ""
echo "🚀 Fazendo deploy..."
gcloud run deploy $SERVICE_NAME \
    --image $LATEST_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

echo ""
echo "✅ Deploy concluído!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "🔗 URL: $SERVICE_URL"
