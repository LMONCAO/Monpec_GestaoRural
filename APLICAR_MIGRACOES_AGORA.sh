#!/bin/bash
# Script para aplicar migrations pendentes no Cloud Run
# Execute no Google Cloud Shell

echo "============================================================"
echo "🔄 APLICAR MIGRATIONS - SISTEMA MONPEC"
echo "============================================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

# Configurar projeto
gcloud config set project $PROJECT_ID

echo "📋 Verificando migrations pendentes..."
echo ""

# Deletar job anterior se existir
gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>/dev/null || true

# Criar job para verificar migrations
echo "📦 Criando job para verificar migrations..."
gcloud run jobs create aplicar-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py showmigrations && echo '---' && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERRO: Não foi possível criar o job."
    exit 1
fi

echo ""
echo "✅ Job criado! Executando migrations..."
echo "⏱️  Aguarde 1-3 minutos..."
echo ""

# Executar o job
gcloud run jobs execute aplicar-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ SUCESSO! Migrations aplicadas!"
    echo "============================================================"
    echo ""
    echo "🔄 Reiniciando serviço..."
    gcloud run services update monpec --region=$REGION --to-latest --quiet
    echo ""
    echo "✅ Serviço reiniciado!"
    echo ""
    echo "🧹 Deseja remover o job temporário? (opcional)"
    echo "   Execute: gcloud run jobs delete aplicar-migrations --region=$REGION"
    echo ""
else
    echo ""
    echo "❌ ERRO ao executar migrations."
    echo ""
    echo "💡 Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migrations\" --limit=50"
    echo ""
    exit 1
fi
