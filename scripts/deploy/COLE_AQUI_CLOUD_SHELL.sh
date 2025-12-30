#!/bin/bash
# Script para criar admin - Cole direto no Cloud Shell

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)

echo "Connection: $CONNECTION_NAME"
echo "Project: $PROJECT_ID"

# ⚠️ SUBSTITUA AQUI PELA SENHA REAL DO BANCO
DB_PASSWORD='Monpec2025!SenhaSegura'

# Deletar job anterior
gcloud run jobs delete create-admin --region us-central1 --quiet 2>&1 || true

# Criar job
gcloud run jobs create create-admin \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --command python \
  --args criar_admin_producao.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp-key-for-admin-creation" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1

echo ""
echo "▶ Executando job..."
gcloud run jobs execute create-admin --region us-central1 --wait








