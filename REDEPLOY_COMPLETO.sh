#!/bin/bash
# Redeploy completo garantindo que atualize

set -e

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/monpec:latest"

echo "========================================"
echo "🔄 REDEPLOY COMPLETO - GARANTINDO ATUALIZAÇÃO"
echo "========================================"
echo ""

# 1. Build com tag única (força novo build)
TIMESTAMP=$(date +%s)
IMAGE_TAG="gcr.io/$PROJECT_ID/monpec:$TIMESTAMP"

echo "1️⃣  Fazendo build com tag única: $IMAGE_TAG"
gcloud builds submit --tag $IMAGE_TAG --tag $IMAGE
echo "✅ Build concluído"
echo ""

# 2. Deploy forçando nova revisão
echo "2️⃣  Fazendo deploy forçando nova revisão..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" \
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080 \
    --no-traffic
echo "✅ Deploy concluído"
echo ""

# 3. Migrar todo o tráfego para nova revisão
echo "3️⃣  Migrando tráfego para nova revisão..."
LATEST_REVISION=$(gcloud run revisions list --service $SERVICE_NAME --region $REGION --limit 1 --format="value(name)" 2>/dev/null | head -1)
if [ -n "$LATEST_REVISION" ]; then
    gcloud run services update-traffic $SERVICE_NAME --region $REGION --to-latest
    echo "✅ Tráfego migrado para: $LATEST_REVISION"
else
    echo "⚠️  Não foi possível migrar tráfego automaticamente"
fi
echo ""

# 4. Verificar
echo "4️⃣  Verificando nova revisão..."
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.latestReadyRevisionName)"
echo ""

echo "========================================"
echo "✅ REDEPLOY CONCLUÍDO!"
echo "========================================"
echo ""
echo "Aguarde 1-2 minutos e teste:"
echo "  https://monpec.com.br"
echo ""
echo "Ver logs:"
echo "  gcloud run services logs read $SERVICE_NAME --region $REGION --limit 20"
echo ""



