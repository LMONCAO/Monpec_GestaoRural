#!/bin/bash
# Script para executar migrações e criar usuário admin no Google Cloud Run
# Uso: gcloud run jobs execute migrate-and-create-admin --region us-central1

set -e

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
SERVICE_NAME="monpec"

echo "=========================================="
echo "EXECUTAR MIGRAÇÕES E CRIAR ADMIN"
echo "=========================================="
echo ""

# Executar migrações
echo "📊 Executando migrações do banco de dados..."
gcloud run jobs execute migrate-and-create-admin \
    --region=$REGION \
    --wait \
    --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

echo ""
echo "✅ Migrações executadas com sucesso!"
echo ""

# Verificar status
echo "Verificando status do job..."
gcloud run jobs describe migrate-and-create-admin --region=$REGION

