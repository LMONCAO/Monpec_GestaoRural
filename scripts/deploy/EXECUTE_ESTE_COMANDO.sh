#!/bin/bash
# ========================================
# COMANDO ÚNICO - COPIE E COLE NO CLOUD SHELL
# Este comando faz TUDO e deixa funcionando
# ========================================

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================"
echo "  INICIANDO DEPLOY COMPLETO"
echo "========================================"

# 1. Configurar
echo "1. Configurando..."
gcloud config set project $PROJECT_ID > /dev/null 2>&1

# 2. Dockerfile
echo "2. Criando Dockerfile..."
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

# 3. Requirements
echo "3. Corrigindo requirements..."
grep -qi "gunicorn" requirements.txt || echo "gunicorn" >> requirements.txt
grep -qi "whitenoise" requirements.txt || echo "whitenoise" >> requirements.txt
grep -qi "psycopg2" requirements.txt || echo "psycopg2-binary" >> requirements.txt

# 4. APIs
echo "4. Habilitando APIs..."
for api in cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com containerregistry.googleapis.com; do
    gcloud services enable $api --quiet 2>&1 | grep -v "already" || true
done

# 5. Build
echo "5. Build (5-10 min)..."
gcloud builds submit --tag ${IMAGE_NAME}:latest --timeout=20m

# 6. Deploy
echo "6. Deploy (2-3 min)..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

gcloud run deploy $SERVICE_NAME \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "$ENV_VARS" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --port=8080

# 7. URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

# 8. Migrações
echo "7. Migrações..."
gcloud run jobs create migrate-monpec \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600 \
    --memory=2Gi \
    --cpu=2 \
    2>&1 | grep -v "already" || true

gcloud run jobs execute migrate-monpec --region $REGION --wait 2>&1 | tail -5

echo ""
echo "========================================"
echo "✅ DEPLOY CONCLUÍDO!"
echo "========================================"
echo ""
echo "URL: $SERVICE_URL"
echo ""
echo "Teste: $SERVICE_URL"
echo ""
















