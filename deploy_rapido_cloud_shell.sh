#!/bin/bash
# Deploy rápido do MONPEC no Google Cloud Run
# Execute este script no Cloud Shell

set -e

PROJECT_ID=$(gcloud config get-value project)
echo "🚀 Deploy MONPEC - Projeto: $PROJECT_ID"
echo ""

# Habilitar APIs
echo "📦 Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com sqladmin.googleapis.com --quiet

# Fazer upload e build
echo "🔨 Fazendo build e deploy..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/monpec:latest

# Deploy no Cloud Run
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy monpec \
    --image gcr.io/$PROJECT_ID/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" \
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "📝 PRÓXIMOS PASSOS:"
echo "1. Configure variáveis de ambiente:"
echo "   gcloud run services update monpec --region us-central1 --update-env-vars 'MERCADOPAGO_ACCESS_TOKEN=APP_USR-...,MERCADOPAGO_PUBLIC_KEY=APP_USR-...,SECRET_KEY=...'"
echo ""
echo "2. Configure domínio:"
echo "   gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1"
echo ""
echo "3. Aplique migrações:"
echo "   gcloud run jobs create migrate-monpec --image gcr.io/$PROJECT_ID/monpec:latest --region us-central1 --command python --args 'manage.py,migrate'"
echo ""


