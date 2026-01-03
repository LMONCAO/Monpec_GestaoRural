#!/bin/bash
# Ver logs do serviço e fazer deploy corrigido
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 Verificando logs do serviço que falhou"
echo "============================================================"
echo ""

# Ver logs da última revisão
REVISION=$(gcloud run revisions list --service=monpec --region=$REGION --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$REVISION" ]; then
    echo "📊 Logs da revisão: $REVISION"
    echo ""
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND resource.labels.revision_name=$REVISION" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -15
else
    echo "📊 Últimos logs do serviço:"
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -15
fi

echo ""
echo "============================================================"
echo "🔄 Fazendo deploy com timeout aumentado"
echo "============================================================"
echo ""

# Fazer deploy com timeout maior e startup probe
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
  --min-instances=0 \
  --max-instances=10

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deploy concluído!"
    echo ""
    echo "🌐 Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
    echo ""
    echo "💡 Se ainda houver erro, verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=monpec\" --limit=30"
else
    echo ""
    echo "❌ Deploy falhou. Verifique os logs acima."
fi
