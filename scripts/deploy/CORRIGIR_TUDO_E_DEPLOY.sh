#!/bin/bash
# Script completo para corrigir tudo e fazer deploy

set -e

echo "=========================================="
echo "🔧 CORRIGINDO TUDO E FAZENDO DEPLOY"
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
if [ -f "gestao_rural/views_exportacao.py" ]; then
    # Verificar se tem import no topo
    if head -30 gestao_rural/views_exportacao.py | grep -qE "^from openpyxl|^import openpyxl"; then
        echo "❌ Encontrado import de openpyxl no topo!"
        # Criar backup
        cp gestao_rural/views_exportacao.py gestao_rural/views_exportacao.py.bak
        
        # Remover linhas que começam com from openpyxl ou import openpyxl
        sed -i '/^from openpyxl/d' gestao_rural/views_exportacao.py
        sed -i '/^import openpyxl/d' gestao_rural/views_exportacao.py
        
        echo "✅ Removido"
    else
        echo "✅ Nenhum import de openpyxl no topo"
    fi
    
    # Verificar se as funções têm lazy import
    if ! grep -A 3 "def exportar_inventario_excel" gestao_rural/views_exportacao.py | grep -q "try:"; then
        echo "⚠️ Função exportar_inventario_excel pode não ter lazy import"
    else
        echo "✅ Funções têm lazy import"
    fi
else
    echo "❌ Arquivo gestao_rural/views_exportacao.py não encontrado!"
fi

echo ""
echo "2️⃣ Corrigindo middleware.py..."
echo "----------------------------------------"
if [ -f "sistema_rural/middleware.py" ]; then
    if grep -q "request.get_host()" sistema_rural/middleware.py; then
        echo "❌ Middleware ainda usa request.get_host()!"
        # Criar backup
        cp sistema_rural/middleware.py sistema_rural/middleware.py.bak
        
        # Substituir request.get_host() por request.META.get('HTTP_HOST', '').split(':')[0]
        sed -i "s/request\.get_host()\.split(':')\[0\]/request.META.get('HTTP_HOST', '').split(':')[0]/g" sistema_rural/middleware.py
        sed -i "s/request\.get_host()/request.META.get('HTTP_HOST', '').split(':')[0]/g" sistema_rural/middleware.py
        
        echo "✅ Corrigido"
    else
        echo "✅ Middleware já está correto"
    fi
else
    echo "❌ Arquivo sistema_rural/middleware.py não encontrado!"
fi

echo ""
echo "3️⃣ Verificando/Criando requirements_producao.txt..."
echo "----------------------------------------"
if [ ! -f "requirements_producao.txt" ]; then
    echo "Criando requirements_producao.txt..."
    cat > requirements_producao.txt << 'EOF'
Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.3
psycopg2-binary==2.9.7
gunicorn==21.2.0
whitenoise==6.6.0
Pillow==10.0.1
reportlab==4.0.4
weasyprint==60.2
pandas==2.1.1
numpy==1.24.3
scikit-learn==1.3.0
matplotlib==3.7.2
seaborn==0.12.2
python-decouple==3.8
celery==5.3.1
redis==5.0.0
django-ratelimit==4.1.0
django-csp==3.7
django-extensions==3.2.3
django-debug-toolbar==4.2.0
django-anymail==10.1
django-redis==5.4.0
django-dbbackup==3.3.0
django-compressor==4.4
django-cachalot==2.6.1
pytest==7.4.2
pytest-django==4.5.2
coverage==7.3.1
openpyxl>=3.1.5
EOF
    echo "✅ requirements_producao.txt criado"
elif ! grep -qE "^openpyxl" requirements_producao.txt; then
    echo "Adicionando openpyxl ao requirements_producao.txt..."
    echo "openpyxl>=3.1.5" >> requirements_producao.txt
    echo "✅ openpyxl adicionado"
else
    echo "✅ openpyxl já está no requirements_producao.txt"
fi

echo ""
echo "4️⃣ Verificando requirements.txt..."
echo "----------------------------------------"
if [ ! -f "requirements.txt" ]; then
    echo "Criando requirements.txt..."
    echo "openpyxl>=3.1.5" > requirements.txt
    echo "✅ requirements.txt criado"
elif ! grep -qE "^openpyxl" requirements.txt; then
    echo "Adicionando openpyxl..."
    echo "openpyxl>=3.1.5" >> requirements.txt
    echo "✅ openpyxl adicionado"
else
    echo "✅ openpyxl já está no requirements.txt"
fi

echo ""
echo "5️⃣ Fazendo build com tag timestamp..."
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
echo "6️⃣ Fazendo deploy no Cloud Run..."
echo "----------------------------------------"
gcloud run deploy $SERVICE_NAME \
    --image $LATEST_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

echo ""
echo "7️⃣ Aguardando serviço ficar pronto..."
echo "----------------------------------------"
sleep 30

echo ""
echo "8️⃣ Testando acesso..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")

echo "URL: $SERVICE_URL"
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço funcionando!"
else
    echo "⚠️ Status: $HTTP_CODE"
    echo ""
    echo "Verificando logs de erro..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=5 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -100
fi

echo ""
echo "=========================================="
echo "✅ PROCESSO CONCLUÍDO"
echo "=========================================="
echo ""





