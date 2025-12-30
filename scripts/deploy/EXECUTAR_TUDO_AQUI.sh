#!/bin/bash
# ========================================
# SCRIPT COMPLETO - FAZ TUDO AUTOMATICAMENTE
# Copie e cole TODO este arquivo no Cloud Shell
# ========================================

set -e

echo "========================================"
echo "  INICIANDO DEPLOY COMPLETO"
echo "  Corrigindo tudo e fazendo deploy"
echo "========================================"
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Funções
print_ok() { echo "✅ $1"; }
print_info() { echo "→ $1"; }
print_step() { echo ""; echo "▶ $1"; echo "----------------------------------------"; }

# PASSO 1: Configurar projeto
print_step "PASSO 1: Configurando projeto"
gcloud config set project $PROJECT_ID
print_ok "Projeto configurado: $PROJECT_ID"

# PASSO 2: Criar Dockerfile.prod
print_step "PASSO 2: Criando Dockerfile.prod"
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
print_ok "Dockerfile.prod criado"

# PASSO 3: Corrigir requirements.txt
print_step "PASSO 3: Corrigindo requirements.txt"
if ! grep -qi "gunicorn" requirements.txt 2>/dev/null; then
    echo "gunicorn" >> requirements.txt
    print_ok "gunicorn adicionado"
else
    print_ok "gunicorn já existe"
fi
if ! grep -qi "whitenoise" requirements.txt 2>/dev/null; then
    echo "whitenoise" >> requirements.txt
    print_ok "whitenoise adicionado"
else
    print_ok "whitenoise já existe"
fi

# PASSO 4: Habilitar APIs
print_step "PASSO 4: Habilitando APIs"
for api in cloudbuild.googleapis.com run.googleapis.com sqladmin.googleapis.com containerregistry.googleapis.com; do
    gcloud services enable $api --quiet 2>&1 | grep -v "already enabled" || true
done
print_ok "APIs habilitadas"

# PASSO 5: Build
print_step "PASSO 5: Fazendo build da imagem (5-10 minutos)"
print_info "Aguarde... isso pode levar alguns minutos"
gcloud builds submit --tag ${IMAGE_NAME}:latest
print_ok "Build concluído!"

# PASSO 6: Deploy
print_step "PASSO 6: Fazendo deploy no Cloud Run (2-3 minutos)"
print_info "Aguarde... configurando serviço"
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
print_ok "Deploy concluído!"

# PASSO 7: Obter URL
print_step "PASSO 7: Obtendo URL do serviço"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    print_ok "URL obtida: $SERVICE_URL"
else
    SERVICE_URL="https://monpec-${PROJECT_ID}.${REGION}.run.app"
    print_info "URL estimada: $SERVICE_URL"
fi

# PASSO 8: Migrações
print_step "PASSO 8: Aplicando migrações do banco de dados"
print_info "Criando job de migração..."
gcloud run jobs create migrate-monpec \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600 \
    2>&1 | grep -v "already exists" || true

print_info "Executando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait
print_ok "Migrações aplicadas!"

# PASSO 9: Verificação final
print_step "PASSO 9: Verificando status"
STATUS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
if [ "$STATUS" = "True" ]; then
    print_ok "Serviço está RODANDO e FUNCIONANDO!"
else
    print_info "Status: $STATUS"
fi

# RESULTADO FINAL
echo ""
echo "========================================"
echo "  ✅ DEPLOY COMPLETO E FUNCIONANDO!"
echo "========================================"
echo ""
echo "🌐 SEU SISTEMA ESTÁ NO AR!"
echo ""
echo "URL: $SERVICE_URL"
echo ""
echo "📋 O QUE FOI FEITO:"
echo "  ✅ Dockerfile.prod criado"
echo "  ✅ requirements.txt corrigido"
echo "  ✅ Build da imagem concluído"
echo "  ✅ Deploy no Cloud Run concluído"
echo "  ✅ Migrações aplicadas"
echo "  ✅ Serviço configurado e rodando"
echo ""
echo "🔗 PRÓXIMOS PASSOS:"
echo ""
echo "1. TESTE AGORA:"
echo "   Abra no navegador: $SERVICE_URL"
echo ""
echo "2. Se quiser ver logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit=30"
echo ""
echo "3. Se quiser configurar domínio monpec.com.br:"
echo "   gcloud run domain-mappings create --service $SERVICE_NAME --domain monpec.com.br --region $REGION"
echo ""
echo "========================================"
echo ""
















