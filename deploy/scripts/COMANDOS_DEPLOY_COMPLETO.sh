#!/bin/bash
# Script completo de deploy - Execute após fazer upload do código

echo "🚀 MONPEC - Deploy Completo no Google Cloud"
echo "============================================"
echo ""

# Verificar se está na pasta correta
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Você precisa estar na pasta Monpec_projetista"
    echo "   Execute: cd Monpec_projetista"
    exit 1
fi

# Configurações
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="Monpec2025!"

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)")
echo "✅ Connection Name: $CONNECTION_NAME"
echo ""

# Gerar SECRET_KEY
echo "🔑 Gerando SECRET_KEY..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "✅ SECRET_KEY gerada"
echo ""

# PASSO 1: Build da imagem
echo "📋 PASSO 1/4: Build da imagem Docker..."
echo "⏳ Isso pode levar 10-15 minutos..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Erro no build. Verifique os logs acima."
    exit 1
fi

echo "✅ Build concluído!"
echo ""

# PASSO 2: Deploy no Cloud Run
echo "📋 PASSO 2/4: Deploy no Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DEBUG=False,\
        DB_NAME=$DB_NAME,\
        DB_USER=$DB_USER,\
        DB_PASSWORD=$DB_PASSWORD,\
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
        SECRET_KEY=$SECRET_KEY \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10

if [ $? -ne 0 ]; then
    echo "❌ Erro no deploy. Verifique os logs acima."
    exit 1
fi

# Obter URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
CLOUD_RUN_HOST=$(echo $SERVICE_URL | sed 's|https://||')

echo "✅ Deploy concluído!"
echo "🌐 URL: $SERVICE_URL"
echo ""

# Atualizar CLOUD_RUN_HOST
echo "📋 Atualizando CLOUD_RUN_HOST..."
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars CLOUD_RUN_HOST=$CLOUD_RUN_HOST

echo "✅ CLOUD_RUN_HOST atualizado!"
echo ""

# PASSO 3: Criar job de migração
echo "📋 PASSO 3/4: Criando job de migração..."
gcloud run jobs create migrate-db \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --region $REGION \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars \
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
        DB_NAME=$DB_NAME,\
        DB_USER=$DB_USER,\
        DB_PASSWORD=$DB_PASSWORD,\
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,\
        SECRET_KEY=$SECRET_KEY \
    --command python \
    --args manage.py,migrate \
    --max-retries=1 \
    --memory=512Mi \
    --cpu=1

# PASSO 4: Executar migrações
echo "📋 PASSO 4/4: Executando migrações..."
gcloud run jobs execute migrate-db --region $REGION

echo "⏳ Aguardando conclusão..."
sleep 15

# Ver status
echo "📋 Status da execução:"
gcloud run jobs executions list --job=migrate-db --region $REGION --limit=1

echo ""
echo "🎉 DEPLOY COMPLETO!"
echo ""
echo "🌐 Seu site está em: $SERVICE_URL"
echo ""
echo "📋 Comandos úteis:"
echo "   Ver logs: gcloud run services logs tail $SERVICE_NAME --region $REGION"
echo "   Ver status: gcloud run services describe $SERVICE_NAME --region $REGION"
echo ""







