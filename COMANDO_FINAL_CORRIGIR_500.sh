#!/bin/bash
# COMANDO FINAL PARA CORRIGIR ERRO 500
# Copie TODO este conteúdo e cole no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔍 PASSO 1: Verificando logs do job que falhou"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -10

echo ""
echo "============================================================"
echo "🔧 PASSO 2: Aplicando migrations (versão robusta)"
echo "============================================================"
echo ""

# Limpar job anterior
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

# Criar job melhorado
echo "📦 Criando job..."
gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo ""
echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute corrigir-500 --region=$REGION --wait

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Job falhou. Ver logs acima ou execute:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500\" --limit=30"
    exit 1
fi

# Limpar
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "============================================================"
echo "🔄 PASSO 3: Fazendo deploy do serviço"
echo "============================================================"
echo ""

gcloud run deploy $SERVICE_NAME \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --add-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --allow-unauthenticated \
  --quiet

echo ""
echo "============================================================"
echo "✅ CONCLUÍDO!"
echo "============================================================"
echo ""
echo "🌐 Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
echo ""
