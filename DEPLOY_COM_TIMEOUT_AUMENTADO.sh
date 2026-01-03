#!/bin/bash
# Deploy com timeout aumentado e configurações otimizadas
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 Verificando logs da última tentativa"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=10 --format="value(textPayload)" 2>/dev/null | tail -5

echo ""
echo "============================================================"
echo "🔄 Fazendo deploy com configurações otimizadas"
echo "============================================================"
echo ""

# Deploy com timeout maior e sem throttling de CPU
gcloud run deploy monpec \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --allow-unauthenticated \
  --port=8080 \
  --no-cpu-throttling

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deploy concluído!"
    echo ""
    echo "⏱️  Aguarde 1-2 minutos para o serviço inicializar..."
    echo ""
    echo "🌐 Depois teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
    echo ""
    echo "💡 Se ainda houver erro, verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=monpec\" --limit=30"
else
    echo ""
    echo "❌ Deploy falhou. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -15
fi
