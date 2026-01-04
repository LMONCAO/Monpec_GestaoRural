#!/bin/bash
# Build e Deploy com Dockerfile.prod especificado explicitamente

cd ~/Monpec_GestaoRural

# Build com Dockerfile.prod explicitamente
echo "🔨 Fazendo build com Dockerfile.prod..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/sistema-rural:latest \
    --timeout=1800s \
    -f Dockerfile.prod \
    .

# Deploy
echo "🚀 Fazendo deploy..."
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/sistema-rural:latest \
    --region=us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,DJANGO_SUPERUSER_PASSWORD=L6171r12@@,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural,DEMO_USER_PASSWORD=monpec" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=900 \
    --max-instances=10 \
    --min-instances=0

echo "✅ Pronto!"


