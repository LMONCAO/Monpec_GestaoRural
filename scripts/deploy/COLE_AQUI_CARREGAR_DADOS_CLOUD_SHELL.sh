#!/bin/bash
# COLE ESTE COMANDO NO GOOGLE CLOUD SHELL
# Copie TODO o conteúdo e cole no Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec:latest"
FONTE="sincronizar"
USUARIO_ID="1"

echo "============================================================"
echo "📊 CARREGAR DADOS DO BANCO - SISTEMA MONPEC"
echo "============================================================"
echo ""

gcloud config set project $PROJECT_ID
gcloud run jobs delete carregar-dados-banco --region=$REGION --quiet 2>/dev/null || true

echo "📦 Criando Cloud Run Job..."
gcloud run jobs create carregar-dados-banco \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="manage.py,carregar_dados_banco,--fonte,$FONTE,--usuario-id,$USUARIO_ID" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=1800

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Job criado! Executando..."
    echo "⏱️  Aguarde 2-5 minutos..."
    echo ""
    gcloud run jobs execute carregar-dados-banco --region=$REGION --wait
    echo ""
    echo "✅ Processo concluído!"
else
    echo "❌ Erro ao criar job"
    exit 1
fi

