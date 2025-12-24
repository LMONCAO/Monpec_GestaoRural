#!/bin/bash
# Script para ATUALIZAR sistema existente no Google Cloud Run

set -e

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE="gcr.io/$PROJECT_ID/monpec:latest"
JOB_NAME="migrate-monpec"

echo "========================================"
echo "🔄 ATUALIZANDO SISTEMA EXISTENTE"
echo "========================================"
echo "Projeto: $PROJECT_ID"
echo "Serviço: $SERVICE_NAME"
echo "Região: $REGION"
echo ""

# 1. Build da nova imagem
echo "🔨 1/4 Fazendo build da nova imagem..."
gcloud builds submit --tag $IMAGE
echo "✅ Build concluído"
echo ""

# 2. Deploy (atualiza serviço existente)
echo "🚀 2/4 Atualizando serviço Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE \
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
    --port 8080
echo "✅ Serviço atualizado"
echo ""

# 3. Atualizar job de migração
echo "🗄️  3/4 Atualizando job de migração..."
echo "Atualizando imagem do job..."
gcloud run jobs update $JOB_NAME \
    --image $IMAGE \
    --region $REGION

echo "Copiando variáveis de ambiente do serviço para o job..."
SERVICE_ENV=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null)

if [ -n "$SERVICE_ENV" ]; then
    echo "Atualizando job com variáveis do serviço..."
    gcloud run jobs update $JOB_NAME --region $REGION --update-env-vars "$SERVICE_ENV"
    echo "✅ Job atualizado com variáveis"
else
    echo "⚠️  Não foi possível obter variáveis do serviço"
    echo "Atualize manualmente o job com as variáveis de ambiente necessárias"
fi
echo ""

# 4. Executar migrações
echo "🔄 4/4 Executando migrações..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
    echo "========================================"
else
    echo ""
    echo "⚠️  Migração falhou. Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --limit 50"
fi
echo ""

# Resumo
echo "📋 Resumo:"
echo "  ✅ Build: Concluído"
echo "  ✅ Deploy: Concluído"
echo "  ✅ Job atualizado: Concluído"
echo "  ✅ Migrações: Executadas"
echo ""
echo "🔗 URL do serviço:"
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null
echo ""
echo "📊 Ver logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit 50"
echo ""



