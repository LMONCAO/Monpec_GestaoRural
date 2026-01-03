#!/bin/bash
# Script final para corrigir erro 500 - verifica e corrige tudo

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔧 CORREÇÃO FINAL DO ERRO 500"
echo "=========================================="
echo ""

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando logs de erro mais recentes..."
echo "----------------------------------------"
echo "Buscando últimos 5 erros..."
LATEST_ERROR=$(gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=1 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID)

if [ -n "$LATEST_ERROR" ]; then
    echo "Último erro encontrado:"
    echo "$LATEST_ERROR" | head -30
else
    echo "Nenhum erro encontrado nos logs recentes"
fi

echo ""
echo "2️⃣ Verificando se código foi atualizado..."
echo "----------------------------------------"
echo "Verificando views_exportacao.py..."
if [ -f "gestao_rural/views_exportacao.py" ]; then
    if head -20 gestao_rural/views_exportacao.py | grep -qE "^from openpyxl|^import openpyxl"; then
        echo "❌ AINDA TEM IMPORTS DE OPENPYXL NO TOPO!"
        echo "Corrigindo..."
        cp gestao_rural/views_exportacao.py gestao_rural/views_exportacao.py.bak
        sed -i '/^from openpyxl/d' gestao_rural/views_exportacao.py
        sed -i '/^import openpyxl/d' gestao_rural/views_exportacao.py
        echo "✅ Corrigido"
    else
        echo "✅ views_exportacao.py está correto (sem imports no topo)"
    fi
else
    echo "⚠️ Arquivo gestao_rural/views_exportacao.py não encontrado no Cloud Shell"
fi

echo ""
echo "3️⃣ Verificando requirements_producao.txt..."
echo "----------------------------------------"
if [ -f "requirements_producao.txt" ]; then
    if grep -qE "^openpyxl" requirements_producao.txt; then
        echo "✅ openpyxl está no requirements_producao.txt"
    else
        echo "❌ openpyxl NÃO está no requirements_producao.txt!"
        echo "Adicionando..."
        echo "openpyxl>=3.1.5" >> requirements_producao.txt
        echo "✅ Adicionado"
    fi
else
    echo "❌ requirements_producao.txt não encontrado!"
    echo "Criando..."
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
fi

echo ""
echo "4️⃣ Fazendo novo build com código corrigido..."
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
    echo ""
    echo "Verificando logs de erro novamente..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -100
fi

echo ""
echo "=========================================="
echo "✅ PROCESSO CONCLUÍDO"
echo "=========================================="
echo ""





