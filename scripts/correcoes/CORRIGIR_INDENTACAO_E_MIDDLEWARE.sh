#!/bin/bash
# Corrigir erro de indentação e middleware

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔧 CORRIGINDO INDENTAÇÃO E MIDDLEWARE"
echo "=========================================="

gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Restaurando arquivo do backup (se existir)..."
if [ -f "gestao_rural/views_relatorios_rastreabilidade.py.bak" ]; then
    cp gestao_rural/views_relatorios_rastreabilidade.py.bak gestao_rural/views_relatorios_rastreabilidade.py
    echo "✅ Arquivo restaurado do backup"
fi

echo ""
echo "2️⃣ Corrigindo views_relatorios_rastreabilidade.py..."
if [ -f "gestao_rural/views_relatorios_rastreabilidade.py" ]; then
    # Remover imports do topo
    sed -i '/^from openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
    sed -i '/^import openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
    
    # Verificar se há erro de sintaxe
    python3 -m py_compile gestao_rural/views_relatorios_rastreabilidade.py 2>&1 | head -20
    if [ $? -eq 0 ]; then
        echo "✅ Arquivo sem erros de sintaxe"
    else
        echo "⚠️ Ainda há erros. Tentando corrigir..."
        # Tentar restaurar do backup novamente
        if [ -f "gestao_rural/views_relatorios_rastreabilidade.py.bak" ]; then
            cp gestao_rural/views_relatorios_rastreabilidade.py.bak gestao_rural/views_relatorios_rastreabilidade.py
            sed -i '/^from openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
            sed -i '/^import openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
        fi
    fi
fi

echo ""
echo "3️⃣ Corrigindo middleware.py..."
if [ -f "sistema_rural/middleware.py" ]; then
    if grep -q "request.get_host()" sistema_rural/middleware.py; then
        echo "Corrigindo middleware..."
        cp sistema_rural/middleware.py sistema_rural/middleware.py.bak
        sed -i "s/request\.get_host()\.split(':')\[0\]/request.META.get('HTTP_HOST', '').split(':')[0]/g" sistema_rural/middleware.py
        sed -i "s/request\.get_host()/request.META.get('HTTP_HOST', '').split(':')[0]/g" sistema_rural/middleware.py
        echo "✅ Middleware corrigido"
    else
        echo "✅ Middleware já está correto"
    fi
fi

echo ""
echo "4️⃣ Garantindo requirements_producao.txt..."
grep -q "^openpyxl" requirements_producao.txt || echo "openpyxl>=3.1.5" >> requirements_producao.txt

echo ""
echo "5️⃣ Fazendo build..."
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
echo "Buildando: $IMAGE_TAG"
gcloud builds submit --tag $IMAGE_TAG

if [ $? -eq 0 ]; then
    echo "✅ Build concluído"
    gcloud container images add-tag $IMAGE_TAG gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --quiet
    echo "✅ Tag 'latest' atualizada"
else
    echo "❌ Erro no build"
    exit 1
fi

echo ""
echo "6️⃣ Fazendo deploy..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

echo ""
echo "✅ Deploy concluído!"





