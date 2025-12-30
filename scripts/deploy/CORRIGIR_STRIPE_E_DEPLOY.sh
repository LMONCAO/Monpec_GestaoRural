#!/bin/bash
# Corrigir importação de stripe e fazer deploy

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔧 CORRIGINDO STRIPE E DEPLOY"
echo "=========================================="

gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Corrigindo views_assinaturas.py..."
if [ -f "gestao_rural/views_assinaturas.py" ]; then
    # Verificar se tem import de stripe_client
    if grep -q "from .services import stripe_client" gestao_rural/views_assinaturas.py; then
        echo "Removendo import de stripe_client..."
        cp gestao_rural/views_assinaturas.py gestao_rural/views_assinaturas.py.bak
        # Remover stripe_client da importação
        sed -i "s/from .services import stripe_client, notificacoes/from .services import notificacoes/g" gestao_rural/views_assinaturas.py
        sed -i "s/from .services import notificacoes, stripe_client/from .services import notificacoes/g" gestao_rural/views_assinaturas.py
        echo "✅ Import de stripe_client removido"
    else
        echo "✅ Já está correto (sem import de stripe_client)"
    fi
fi

echo ""
echo "2️⃣ Corrigindo services/__init__.py se necessário..."
if [ -f "gestao_rural/services/__init__.py" ]; then
    if grep -q "stripe_client" gestao_rural/services/__init__.py; then
        echo "Removendo stripe_client do __init__.py..."
        cp gestao_rural/services/__init__.py gestao_rural/services/__init__.py.bak
        sed -i '/stripe_client/d' gestao_rural/services/__init__.py
        echo "✅ Corrigido"
    fi
fi

echo ""
echo "3️⃣ Garantindo requirements_producao.txt..."
# Adicionar stripe apenas se realmente necessário (mas vamos tentar remover a dependência primeiro)
if ! grep -q "^stripe" requirements_producao.txt; then
    echo "⚠️ stripe não está no requirements. Adicionando como fallback..."
    echo "stripe>=7.0.0" >> requirements_producao.txt
fi

# Garantir openpyxl também
grep -q "^openpyxl" requirements_producao.txt || echo "openpyxl>=3.1.5" >> requirements_producao.txt

echo ""
echo "4️⃣ Fazendo build..."
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
echo "5️⃣ Fazendo deploy..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

echo ""
echo "6️⃣ Testando..."
sleep 30
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" --project=$PROJECT_ID)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")
echo "URL: $SERVICE_URL"
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "301" ] && [ "$HTTP_CODE" != "302" ]; then
    echo ""
    echo "Verificando logs..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -100
fi

echo ""
echo "✅ Processo concluído!"





