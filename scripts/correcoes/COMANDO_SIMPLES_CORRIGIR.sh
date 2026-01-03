#!/bin/bash
# Comando simples para corrigir e fazer deploy

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "🔧 Corrigindo e fazendo deploy..."

gcloud config set project $PROJECT_ID

# Corrigir views_relatorios_rastreabilidade.py
if [ -f "gestao_rural/views_relatorios_rastreabilidade.py" ]; then
    echo "Removendo imports de openpyxl do topo..."
    cp gestao_rural/views_relatorios_rastreabilidade.py gestao_rural/views_relatorios_rastreabilidade.py.bak
    sed -i '/^from openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
    sed -i '/^import openpyxl/d' gestao_rural/views_relatorios_rastreabilidade.py
    echo "✅ Corrigido"
fi

# Garantir requirements_producao.txt
if [ ! -f "requirements_producao.txt" ] || ! grep -qE "^openpyxl" requirements_producao.txt; then
    echo "openpyxl>=3.1.5" >> requirements_producao.txt
fi

# Build e deploy
TIMESTAMP=$(date +%Y%m%d%H%M%S)
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP
gcloud container images add-tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP gcr.io/$PROJECT_ID/$SERVICE_NAME:latest --quiet

gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms"

echo "✅ Deploy concluído!"





