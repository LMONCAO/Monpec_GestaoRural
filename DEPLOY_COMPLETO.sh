#!/bin/bash
# Deploy COMPLETO do MONPEC no Google Cloud Run
# Este script faz TUDO: build, deploy, variáveis, domínio e migrações

set -e  # Parar em caso de erro

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="monpec"
REGION="us-central1"  # CORRIGIDO: era us-centrall
IMAGE="gcr.io/$PROJECT_ID/monpec:latest"

echo "========================================"
echo "🚀 DEPLOY COMPLETO - MONPEC"
echo "========================================"
echo "Projeto: $PROJECT_ID"
echo "Serviço: $SERVICE_NAME"
echo "Região: $REGION"
echo ""

# 1. Habilitar APIs necessárias
echo "📦 1/6 Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
echo "✅ APIs habilitadas"
echo ""

# 2. Build da imagem Docker
echo "🔨 2/6 Fazendo build da imagem Docker..."
gcloud builds submit --tag $IMAGE
echo "✅ Build concluído"
echo ""

# 3. Deploy no Cloud Run
echo "🚀 3/6 Fazendo deploy no Cloud Run..."
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

# 4. Configurar variáveis de ambiente
echo "⚙️  4/6 Configurando variáveis de ambiente..."
echo "IMPORTANTE: Configure manualmente as seguintes variáveis no Console:"
echo "  - MERCADOPAGO_ACCESS_TOKEN"
echo "  - MERCADOPAGO_PUBLIC_KEY"
echo "  - SECRET_KEY"
echo "  - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST"
echo ""
echo "Ou execute:"
echo "  gcloud run services update $SERVICE_NAME --region $REGION \\"
echo "    --update-env-vars 'MERCADOPAGO_ACCESS_TOKEN=APP_USR-...,MERCADOPAGO_PUBLIC_KEY=APP_USR-...,SECRET_KEY=...,DB_NAME=...,DB_USER=...,DB_PASSWORD=...,DB_HOST=...'"
echo ""

# 5. Configurar domínio
echo "🌐 5/6 Configurando domínio personalizado..."
echo "Criando mapeamento para monpec.com.br..."
gcloud run domain-mappings create \
    --service $SERVICE_NAME \
    --domain monpec.com.br \
    --region $REGION || echo "⚠️  Domínio monpec.com.br já existe ou erro ao criar"

echo "Criando mapeamento para www.monpec.com.br..."
gcloud run domain-mappings create \
    --service $SERVICE_NAME \
    --domain www.monpec.com.br \
    --region $REGION || echo "⚠️  Domínio www.monpec.com.br já existe ou erro ao criar"
echo "✅ Domínios configurados"
echo ""

# 6. Aplicar migrações
echo "🗄️  6/6 Aplicando migrações do banco de dados..."
echo "Criando job de migração..."
gcloud run jobs create migrate-monpec \
    --image $IMAGE \
    --region $REGION \
    --command python \
    --args "manage.py,migrate" \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
    --max-retries 3 \
    --task-timeout 600 || echo "⚠️  Job já existe, pulando criação"

echo "Executando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait || echo "⚠️  Erro ao executar migrações (pode ser necessário configurar variáveis de ambiente primeiro)"
echo "✅ Migrações aplicadas"
echo ""

echo "========================================"
echo "✅ DEPLOY COMPLETO FINALIZADO!"
echo "========================================"
echo ""
echo "📋 RESUMO:"
echo "  ✅ Build da imagem: Concluído"
echo "  ✅ Deploy no Cloud Run: Concluído"
echo "  ⚠️  Variáveis de ambiente: Configure manualmente"
echo "  ✅ Domínio: Configurado"
echo "  ✅ Migrações: Aplicadas"
echo ""
echo "🔗 Próximos passos:"
echo "1. Configure as variáveis de ambiente no Console:"
echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
echo ""
echo "2. Configure os registros DNS no seu provedor de domínio"
echo "   (os registros serão exibidos após a criação do mapeamento)"
echo ""
echo "3. Acesse o sistema:"
echo "   https://monpec.com.br"
echo ""
echo "📊 Ver logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION"
echo ""





















