#!/bin/bash
# Script de deploy para executar no Google Cloud Shell
# Projeto: monpec-sistema-rural

set -e  # Parar em caso de erro

echo "========================================"
echo "DEPLOY MONPEC - Google Cloud Run"
echo "========================================"
echo ""

# Verificar se está no Cloud Shell
if [ -z "$CLOUD_SHELL" ]; then
    echo "AVISO: Este script é otimizado para Cloud Shell"
fi

# Verificar projeto
PROJECT_ID=$(gcloud config get-value project)
echo "Projeto atual: $PROJECT_ID"
echo ""

# Habilitar APIs necessárias
echo "Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet

echo ""
echo "========================================"
echo "Iniciando build e deploy..."
echo "========================================"
echo ""

# Fazer build e deploy usando Cloud Build
gcloud builds submit --config cloudbuild.yaml

echo ""
echo "========================================"
echo "DEPLOY CONCLUIDO!"
echo "========================================"
echo ""
echo "Próximos passos:"
echo "1. Configure as variáveis de ambiente no Cloud Run:"
echo "   - MERCADOPAGO_ACCESS_TOKEN"
echo "   - MERCADOPAGO_PUBLIC_KEY"
echo "   - SECRET_KEY"
echo "   - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST"
echo ""
echo "2. Configure o domínio personalizado:"
echo "   gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1"
echo "   gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1"
echo ""
echo "3. Aplique as migrações:"
echo "   gcloud run jobs create migrate-monpec --image gcr.io/$PROJECT_ID/monpec:latest --region us-central1 --command python --args 'manage.py,migrate' --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'"
echo "   gcloud run jobs execute migrate-monpec --region us-central1"
echo ""
echo "Acesse o console: https://console.cloud.google.com/run/detail/us-central1/monpec"
echo ""


