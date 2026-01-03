#!/bin/bash
# Script RÁPIDO de deploy para Google Cloud Platform
# Execute no Google Cloud Shell

set -e

echo "========================================"
echo "DEPLOY RÁPIDO - MONPEC GCP"
echo "========================================"
echo ""

# Verificar diretório
if [ ! -f "manage.py" ]; then
    echo "ERRO: Execute no diretório raiz do projeto!"
    exit 1
fi

# Obter projeto
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "ERRO: Configure o projeto: gcloud config set project SEU_PROJETO"
    exit 1
fi

echo "Projeto: $PROJECT_ID"
echo ""

# Build e Deploy
echo "Fazendo build e deploy..."
IMAGE_TAG="gcr.io/${PROJECT_ID}/monpec:latest"

# Usar Dockerfile.prod se existir - gcloud usa Dockerfile por padrão
if [ -f "Dockerfile.prod" ]; then
    echo "Usando Dockerfile.prod"
    # Backup do Dockerfile se existir
    if [ -f "Dockerfile" ]; then
        cp Dockerfile Dockerfile.backup
    fi
    # Usar Dockerfile.prod
    cp Dockerfile.prod Dockerfile
    USE_DOCKERFILE_PROD=true
else
    USE_DOCKERFILE_PROD=false
fi

gcloud builds submit --tag "$IMAGE_TAG" --quiet

# Restaurar Dockerfile se necessário
if [ "$USE_DOCKERFILE_PROD" = true ] && [ -f "Dockerfile.backup" ]; then
    mv Dockerfile.backup Dockerfile
fi

gcloud run deploy monpec \
    --image "$IMAGE_TAG" \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
    --memory=1Gi \
    --quiet

SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format="value(status.url)")

echo ""
echo "========================================"
echo "✓ DEPLOY CONCLUÍDO!"
echo "========================================"
echo ""
echo "URL: $SERVICE_URL"
echo ""
echo "Aplicar migrações:"
echo "  gcloud run jobs create migrate-monpec --image $IMAGE_TAG --region us-central1 --command python --args 'manage.py,migrate,--noinput' --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'"
echo "  gcloud run jobs execute migrate-monpec --region us-central1"
echo ""

