#!/bin/bash
# Script completo para corrigir erro 400 - Execute este script no Cloud Shell

set -e

echo "=========================================="
echo "🔧 CORREÇÃO COMPLETA - ERRO 400"
echo "=========================================="
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
CLOUD_SQL_INSTANCE="monpec-sistema-rural:us-central1:monpec-db"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Adicionando conexão Cloud SQL ao serviço..."
echo "----------------------------------------"
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --add-cloudsql-instances=$CLOUD_SQL_INSTANCE \
    --quiet

echo "✅ Conexão Cloud SQL adicionada"

echo ""
echo "2️⃣ Configurando variáveis de ambiente críticas..."
echo "----------------------------------------"

# Verificar e configurar CLOUD_SQL_CONNECTION_NAME
CURRENT_CLOUD_SQL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" 2>/dev/null || echo "")

if [ -z "$CURRENT_CLOUD_SQL" ] || [ "$CURRENT_CLOUD_SQL" != "$CLOUD_SQL_INSTANCE" ]; then
    echo "Configurando CLOUD_SQL_CONNECTION_NAME..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_INSTANCE" \
        --quiet
    echo "✅ CLOUD_SQL_CONNECTION_NAME configurado"
else
    echo "✅ CLOUD_SQL_CONNECTION_NAME já está configurado corretamente"
fi

# Verificar SECRET_KEY
CURRENT_SECRET_KEY=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='SECRET_KEY')].value)" 2>/dev/null || echo "")

if [ -z "$CURRENT_SECRET_KEY" ]; then
    echo "Configurando SECRET_KEY..."
    NEW_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "SECRET_KEY=$NEW_SECRET_KEY" \
        --quiet
    echo "✅ SECRET_KEY configurada"
else
    echo "✅ SECRET_KEY já está configurada"
fi

# Verificar DJANGO_SETTINGS_MODULE
CURRENT_SETTINGS=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_SETTINGS_MODULE')].value)" 2>/dev/null || echo "")

if [ -z "$CURRENT_SETTINGS" ] || [ "$CURRENT_SETTINGS" != "sistema_rural.settings_gcp" ]; then
    echo "Configurando DJANGO_SETTINGS_MODULE..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
        --quiet
    echo "✅ DJANGO_SETTINGS_MODULE configurado"
else
    echo "✅ DJANGO_SETTINGS_MODULE já está configurado corretamente"
fi

# Verificar DEBUG
CURRENT_DEBUG=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DEBUG')].value)" 2>/dev/null || echo "")

if [ -z "$CURRENT_DEBUG" ] || [ "$CURRENT_DEBUG" != "False" ]; then
    echo "Configurando DEBUG=False..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "DEBUG=False" \
        --quiet
    echo "✅ DEBUG configurado"
else
    echo "✅ DEBUG já está configurado corretamente"
fi

echo ""
echo "3️⃣ Aguardando atualização do serviço..."
echo "----------------------------------------"
sleep 10

echo ""
echo "4️⃣ Testando acesso ao serviço..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)")

echo "URL do serviço: $SERVICE_URL"
echo ""

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço respondendo corretamente (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "400" ]; then
    echo "⚠️ Erro 400 ainda presente"
    echo ""
    echo "Verificando logs recentes..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
        --limit=5 \
        --format="table(timestamp,severity,textPayload)" \
        --project=$PROJECT_ID | head -20
    echo ""
    echo "💡 Se o erro persistir, faça um novo deploy com as correções do código:"
    echo "   gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME"
    echo "   gcloud run deploy $SERVICE_NAME --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --region $REGION"
else
    echo "⚠️ Serviço retornou HTTP $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "✅ CORREÇÕES APLICADAS"
echo "=========================================="
echo ""
echo "📝 Resumo:"
echo "  - Conexão Cloud SQL: ✅ Configurada"
echo "  - CLOUD_SQL_CONNECTION_NAME: ✅ Configurado"
echo "  - SECRET_KEY: ✅ Configurada"
echo "  - DJANGO_SETTINGS_MODULE: ✅ Configurado"
echo "  - DEBUG: ✅ Configurado"
echo ""
echo "🔗 URL do serviço: $SERVICE_URL"
echo ""
echo "⚠️ IMPORTANTE: Se ainda houver erro 400, você precisa fazer um novo deploy"
echo "   com as correções do código (middleware e settings_gcp.py atualizados)"
echo ""





