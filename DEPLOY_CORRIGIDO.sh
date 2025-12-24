#!/bin/bash
# Deploy COMPLETO com região CORRIGIDA
# Região correta: us-central1 (não us-centrall)

set -e

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="monpec"
REGION="us-central1"  # ✅ CORRIGIDO
IMAGE="gcr.io/$PROJECT_ID/monpec:latest"

echo "========================================"
echo "🚀 DEPLOY COMPLETO - MONPEC"
echo "========================================"
echo "Projeto: $PROJECT_ID"
echo "Serviço: $SERVICE_NAME"
echo "Região: $REGION ✅"
echo ""

# 1. Habilitar APIs
echo "📦 1/6 Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com sqladmin.googleapis.com --quiet
echo "✅ APIs habilitadas"
echo ""

# 2. Build
echo "🔨 2/6 Fazendo build..."
gcloud builds submit --tag $IMAGE
echo "✅ Build concluído"
echo ""

# 3. Deploy
echo "🚀 3/6 Fazendo deploy..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE \
    --region $REGION \
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
echo "✅ Deploy concluído"
echo ""

# 4. Domínio
echo "🌐 4/6 Configurando domínio..."
gcloud run domain-mappings create \
    --service $SERVICE_NAME \
    --domain monpec.com.br \
    --region $REGION 2>/dev/null || echo "⚠️  Domínio já existe"
    
gcloud run domain-mappings create \
    --service $SERVICE_NAME \
    --domain www.monpec.com.br \
    --region $REGION 2>/dev/null || echo "⚠️  Domínio já existe"
echo "✅ Domínios configurados"
echo ""

# 5. Migrações
echo "🗄️  5/6 Aplicando migrações..."
gcloud run jobs create migrate-monpec \
    --image $IMAGE \
    --region $REGION \
    --command python \
    --args "manage.py,migrate" \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
    --max-retries 3 \
    --task-timeout 600 2>/dev/null || echo "⚠️  Job já existe"

gcloud run jobs execute migrate-monpec --region $REGION --wait 2>/dev/null || echo "⚠️  Erro ao executar (configure variáveis primeiro)"
echo "✅ Migrações aplicadas"
echo ""

# 6. Resumo
echo "========================================"
echo "✅ DEPLOY CONCLUÍDO!"
echo "========================================"
echo ""
echo "📋 PRÓXIMO PASSO:"
echo "Configure as variáveis de ambiente:"
echo ""
echo "gcloud run services update $SERVICE_NAME --region $REGION \\"
echo "  --update-env-vars 'MERCADOPAGO_ACCESS_TOKEN=APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940,MERCADOPAGO_PUBLIC_KEY=APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3,SECRET_KEY=SUA_SECRET_KEY,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME'"
echo ""
echo "🔗 URL do serviço:"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null || echo "Execute o deploy primeiro"
echo ""



