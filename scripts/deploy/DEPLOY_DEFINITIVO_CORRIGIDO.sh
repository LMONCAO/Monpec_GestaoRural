#!/bin/bash
# Script para fazer deploy definitivo com todas as correções

set -e

echo "=========================================="
echo "🚀 DEPLOY DEFINITIVO - TODAS AS CORREÇÕES"
echo "=========================================="
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando se requirements.txt tem openpyxl..."
echo "----------------------------------------"
if [ -f "requirements.txt" ]; then
    if grep -q "openpyxl" requirements.txt; then
        echo "✅ openpyxl encontrado:"
        grep "openpyxl" requirements.txt
    else
        echo "⚠️ openpyxl não encontrado. Adicionando..."
        echo "openpyxl>=3.1.5" >> requirements.txt
    fi
else
    echo "❌ requirements.txt não encontrado. Criando..."
    cat > requirements.txt << EOF
Django>=4.2.7,<5.0
psycopg2-binary>=2.9.9
gunicorn>=21.2.0
python-decouple>=3.8
whitenoise>=6.6.0
openpyxl>=3.1.5
reportlab>=4.0.0
Pillow>=10.0.0
django-extensions>=3.2.0
EOF
fi

echo ""
echo "2️⃣ Verificando se views_exportacao.py está correto..."
echo "----------------------------------------"
if grep -q "^from openpyxl" gestao_rural/views_exportacao.py 2>/dev/null; then
    echo "❌ ERRO: views_exportacao.py ainda tem import de openpyxl no topo!"
    echo "   Removendo..."
    # Isso não deve acontecer, mas vamos garantir
    sed -i '/^from openpyxl/d' gestao_rural/views_exportacao.py
    sed -i '/^import openpyxl/d' gestao_rural/views_exportacao.py
    echo "✅ Corrigido"
else
    echo "✅ views_exportacao.py está correto (sem import no topo)"
fi

echo ""
echo "3️⃣ Verificando se middleware.py está correto..."
echo "----------------------------------------"
if grep -q "request.get_host()" sistema_rural/middleware.py 2>/dev/null; then
    echo "❌ ERRO: middleware.py ainda usa request.get_host()!"
    echo "   Isso precisa ser corrigido manualmente"
else
    echo "✅ middleware.py está correto"
fi

echo ""
echo "4️⃣ Fazendo build com tag timestamp..."
echo "----------------------------------------"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
LATEST_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "Buildando: $IMAGE_TAG"
gcloud builds submit --tag $IMAGE_TAG

if [ $? -eq 0 ]; then
    echo "✅ Build concluído"
    gcloud container images add-tag $IMAGE_TAG $LATEST_TAG --quiet
    echo "✅ Tag 'latest' atualizada"
else
    echo "❌ Erro no build"
    exit 1
fi

echo ""
echo "5️⃣ Fazendo deploy no Cloud Run..."
echo "----------------------------------------"
gcloud run deploy $SERVICE_NAME \
    --image $LATEST_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

if [ $? -eq 0 ]; then
    echo "✅ Deploy concluído"
else
    echo "❌ Erro no deploy"
    exit 1
fi

echo ""
echo "6️⃣ Aguardando serviço ficar pronto..."
echo "----------------------------------------"
sleep 30

echo ""
echo "7️⃣ Testando acesso..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")

echo "URL: $SERVICE_URL"
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço funcionando!"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Erro 500 ainda presente"
    echo "Verificando logs..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -50
else
    echo "⚠️ Status: $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "✅ DEPLOY CONCLUÍDO"
echo "=========================================="
echo ""
echo "🔗 URL: $SERVICE_URL"
echo ""





