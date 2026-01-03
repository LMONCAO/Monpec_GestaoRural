#!/bin/bash
# Script para corrigir arquivos no Cloud Shell e fazer deploy

set -e

echo "=========================================="
echo "🔧 CORRIGINDO ARQUIVOS E DEPLOY FINAL"
echo "=========================================="
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Corrigindo views_exportacao.py..."
echo "----------------------------------------"
# Verificar se tem import de openpyxl no topo
if grep -q "^from openpyxl\|^import openpyxl" gestao_rural/views_exportacao.py 2>/dev/null; then
    echo "❌ Encontrado import de openpyxl no topo. Removendo..."
    # Remover linhas que começam com from openpyxl ou import openpyxl
    sed -i '/^from openpyxl/d' gestao_rural/views_exportacao.py
    sed -i '/^import openpyxl/d' gestao_rural/views_exportacao.py
    echo "✅ Removido"
else
    echo "✅ views_exportacao.py já está correto"
fi

# Verificar se as funções têm lazy import
if ! grep -A 5 "def exportar_inventario_excel" gestao_rural/views_exportacao.py | grep -q "try:"; then
    echo "⚠️ Função exportar_inventario_excel não tem lazy import. Corrigindo..."
    # Isso é complexo, vamos fazer manualmente se necessário
    echo "   (Precisa ser corrigido manualmente ou via upload do arquivo correto)"
fi

echo ""
echo "2️⃣ Corrigindo middleware.py..."
echo "----------------------------------------"
# Verificar se usa request.get_host()
if grep -q "request.get_host()" sistema_rural/middleware.py 2>/dev/null; then
    echo "❌ Middleware ainda usa request.get_host(). Corrigindo..."
    # Substituir request.get_host() por request.META.get('HTTP_HOST')
    sed -i "s/request\.get_host()/request.META.get('HTTP_HOST', '').split(':')[0]/g" sistema_rural/middleware.py
    echo "✅ Corrigido"
else
    echo "✅ middleware.py já está correto"
fi

echo ""
echo "3️⃣ Verificando requirements.txt..."
echo "----------------------------------------"
if [ ! -f "requirements.txt" ]; then
    echo "Criando requirements.txt..."
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
elif ! grep -q "openpyxl" requirements.txt; then
    echo "Adicionando openpyxl ao requirements.txt..."
    echo "openpyxl>=3.1.5" >> requirements.txt
    echo "✅ openpyxl adicionado"
else
    echo "✅ openpyxl já está no requirements.txt"
fi

echo ""
echo "4️⃣ Fazendo build..."
echo "----------------------------------------"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
LATEST_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

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
echo "5️⃣ Fazendo deploy..."
echo "----------------------------------------"
gcloud run deploy $SERVICE_NAME \
    --image $LATEST_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

echo ""
echo "6️⃣ Aguardando e testando..."
echo "----------------------------------------"
sleep 30

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")

echo "URL: $SERVICE_URL"
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço funcionando!"
else
    echo "⚠️ Status: $HTTP_CODE"
    echo "Verificando logs..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -50
fi

echo ""
echo "=========================================="
echo "✅ PROCESSO CONCLUÍDO"
echo "=========================================="
echo ""





