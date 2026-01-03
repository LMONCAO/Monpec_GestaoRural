#!/bin/bash
# Script para corrigir openpyxl e fazer deploy

set -e

echo "=========================================="
echo "🔧 CORRIGINDO openpyxl E FAZENDO DEPLOY"
echo "=========================================="
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando se requirements.txt existe e tem openpyxl..."
echo "----------------------------------------"
if [ -f "requirements.txt" ]; then
    if grep -q "openpyxl" requirements.txt; then
        echo "✅ openpyxl encontrado no requirements.txt:"
        grep "openpyxl" requirements.txt
    else
        echo "⚠️ openpyxl não encontrado. Adicionando..."
        echo "openpyxl>=3.1.5" >> requirements.txt
        echo "✅ openpyxl adicionado"
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
    echo "✅ requirements.txt criado"
fi

echo ""
echo "2️⃣ Fazendo build da imagem..."
echo "----------------------------------------"
echo "Isso pode levar alguns minutos..."
echo "Usando tag com timestamp para forçar novo build..."

# Criar tag com timestamp para forçar novo build
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
LATEST_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "Buildando com tag: $IMAGE_TAG"
gcloud builds submit --tag $IMAGE_TAG

if [ $? -eq 0 ]; then
    echo "✅ Build concluído com sucesso"
    # Marcar também como latest
    gcloud container images add-tag $IMAGE_TAG $LATEST_TAG --quiet
    echo "✅ Tag 'latest' atualizada"
else
    echo "❌ Erro no build"
    exit 1
fi

echo ""
echo "3️⃣ Fazendo deploy no Cloud Run..."
echo "----------------------------------------"
gcloud run deploy $SERVICE_NAME \
    --image $LATEST_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms" \
    --quiet

if [ $? -eq 0 ]; then
    echo "✅ Deploy concluído com sucesso"
else
    echo "❌ Erro no deploy"
    exit 1
fi

echo ""
echo "4️⃣ Aguardando serviço ficar pronto..."
echo "----------------------------------------"
sleep 20

echo ""
echo "5️⃣ Testando acesso ao serviço..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)" \
    --project=$PROJECT_ID)

echo "URL: $SERVICE_URL"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço funcionando! (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "⚠️ Erro 500 ainda presente"
    echo "Verificando logs..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -30
else
    echo "⚠️ Serviço retornou HTTP $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "✅ PROCESSO CONCLUÍDO"
echo "=========================================="
echo ""
echo "🔗 URL: $SERVICE_URL"
echo ""

