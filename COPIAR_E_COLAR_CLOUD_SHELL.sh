#!/bin/bash
# COPIAR E COLAR ESTE ARQUIVO COMPLETO NO CLOUD SHELL
# Este script faz TUDO automaticamente: corrige, configura e faz deploy

set -e

echo "========================================"
echo "  DEPLOY AUTOMÁTICO - CORRIGINDO TUDO"
echo "========================================"

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# 1. Configurar projeto
echo "1. Configurando projeto..."
gcloud config set project $PROJECT_ID

# 2. Criar Dockerfile.prod
echo "2. Criando Dockerfile.prod..."
cat > Dockerfile.prod << 'EOF'
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends postgresql-client build-essential libpq-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . .
RUN mkdir -p /app/staticfiles /app/media /app/logs
ENV PORT=8080
EXPOSE 8080
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - sistema_rural.wsgi:application
EOF

# 3. Corrigir requirements.txt
echo "3. Corrigindo requirements.txt..."
grep -qi "gunicorn" requirements.txt || echo "gunicorn" >> requirements.txt
grep -qi "whitenoise" requirements.txt || echo "whitenoise" >> requirements.txt

# 4. Habilitar APIs
echo "4. Habilitando APIs..."
for api in cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com containerregistry.googleapis.com; do
    gcloud services enable $api --quiet 2>&1 | grep -v "already enabled" || true
done

# 5. Build
echo "5. Fazendo build (5-10 min)..."
gcloud builds submit --tag ${IMAGE_NAME}:latest

# 6. Deploy
echo "6. Fazendo deploy (2-3 min)..."
gcloud run deploy $SERVICE_NAME \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --memory=1Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

# 7. Obter URL
echo "7. Obtendo URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

# 8. Migrações
echo "8. Aplicando migrações..."
gcloud run jobs create migrate-monpec \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600 \
    2>&1 | grep -v "already exists" || true

gcloud run jobs execute migrate-monpec --region $REGION --wait

echo ""
echo "========================================"
echo "✅ DEPLOY CONCLUÍDO!"
echo "========================================"
echo "URL: $SERVICE_URL"
echo "Teste agora: $SERVICE_URL"
echo "========================================"









