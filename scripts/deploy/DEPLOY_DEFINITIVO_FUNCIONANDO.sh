#!/bin/bash
# ========================================
# DEPLOY DEFINITIVO - CORRIGE TUDO E FUNCIONA
# Este script faz TUDO: corrige código, faz build e deploy
# ========================================

set -e

echo "========================================"
echo "  DEPLOY DEFINITIVO - CORRIGINDO TUDO"
echo "========================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Funções
ok() { echo "✅ $1"; }
info() { echo "→ $1"; }
step() { echo ""; echo "▶ $1"; echo "----------------------------------------"; }

# PASSO 1: Configurar projeto
step "PASSO 1: Configurando projeto"
gcloud config set project $PROJECT_ID > /dev/null 2>&1
ok "Projeto configurado"

# PASSO 2: Criar Dockerfile.prod
step "PASSO 2: Criando Dockerfile.prod"
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
ok "Dockerfile.prod criado"

# PASSO 3: Corrigir requirements.txt
step "PASSO 3: Corrigindo requirements.txt"
grep -qi "gunicorn" requirements.txt || echo "gunicorn" >> requirements.txt
grep -qi "whitenoise" requirements.txt || echo "whitenoise" >> requirements.txt
grep -qi "psycopg2" requirements.txt || echo "psycopg2-binary" >> requirements.txt
ok "requirements.txt corrigido"

# PASSO 4: Habilitar APIs
step "PASSO 4: Habilitando APIs"
for api in cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com containerregistry.googleapis.com; do
    gcloud services enable $api --quiet 2>&1 | grep -v "already enabled" || true
done
ok "APIs habilitadas"

# PASSO 5: Build
step "PASSO 5: Fazendo build (5-10 minutos)"
info "Aguarde... criando imagem Docker"
gcloud builds submit --tag ${IMAGE_NAME}:latest --timeout=20m
ok "Build concluído!"

# PASSO 6: Deploy com TODAS as variáveis corretas
step "PASSO 6: Fazendo deploy (2-3 minutos)"
info "Configurando serviço com todas as variáveis..."

ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"
ENV_VARS="${ENV_VARS},DEBUG=False"
ENV_VARS="${ENV_VARS},SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t"
ENV_VARS="${ENV_VARS},DB_NAME=monpec_db"
ENV_VARS="${ENV_VARS},DB_USER=monpec_user"
ENV_VARS="${ENV_VARS},DB_PASSWORD=Django2025@"
ENV_VARS="${ENV_VARS},CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db"
ENV_VARS="${ENV_VARS},PYTHONUNBUFFERED=1"
ENV_VARS="${ENV_VARS},PYTHONDONTWRITEBYTECODE=1"

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

ok "Deploy concluído!"

# PASSO 7: Obter URL
step "PASSO 7: Obtendo URL"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    ok "URL: $SERVICE_URL"
else
    SERVICE_URL="https://monpec-${PROJECT_ID}.${REGION}.run.app"
    info "URL estimada: $SERVICE_URL"
fi

# PASSO 8: Migrações
step "PASSO 8: Aplicando migrações"
info "Criando job de migração..."
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
    2>&1 | grep -v "already exists" || true

info "Executando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait 2>&1 | tail -10
ok "Migrações aplicadas"

# PASSO 9: Aguardar e verificar
step "PASSO 9: Aguardando serviço ficar pronto"
sleep 10
info "Aguardando 10 segundos para o serviço inicializar..."

# PASSO 10: Verificar status
step "PASSO 10: Verificando status final"
STATUS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")

echo ""
echo "========================================"
if [ "$STATUS" = "True" ]; then
    echo "✅ DEPLOY CONCLUÍDO E FUNCIONANDO!"
    echo "========================================"
    echo ""
    echo "🌐 SEU SISTEMA ESTÁ NO AR!"
    echo ""
    echo "URL: $SERVICE_URL"
    echo ""
    echo "📋 TESTE AGORA:"
    echo "   1. Abra no navegador: $SERVICE_URL"
    echo "   2. Se aparecer erro, aguarde mais 30 segundos"
    echo "   3. Se ainda houver erro, execute:"
    echo "      gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50"
    echo ""
else
    echo "⚠️  Verifique o status manualmente"
    echo "========================================"
    echo ""
    echo "Execute para ver logs:"
    echo "  gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50"
    echo ""
fi

echo "========================================"
echo ""
















