#!/bin/bash
# Solução FINAL para migration duplicada
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 Verificando logs do erro anterior"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -10

echo ""
echo "============================================================"
echo "🔧 SOLUÇÃO: Marcar migration como fake (passo a passo)"
echo "============================================================"
echo ""

# Limpar
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true

# Passo 1: Marcar migration 0034 como fake
echo "📦 Passo 1: Marcando migration 0034 como aplicada (fake)..."
gcloud run jobs create corrigir-migration \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,gestao_rural,0034_financeiro_reestruturado,--fake" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=600

echo "⏱️  Executando passo 1..."
gcloud run jobs execute corrigir-migration --region=$REGION --wait

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro no passo 1. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -15
    gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true
    exit 1
fi

echo "✅ Passo 1 concluído!"
echo ""

# Passo 2: Aplicar migrations restantes
echo "📦 Passo 2: Aplicando migrations restantes..."
gcloud run jobs update corrigir-migration \
  --region=$REGION \
  --args="manage.py,migrate,--noinput" \
  --quiet

gcloud run jobs execute corrigir-migration --region=$REGION --wait

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro no passo 2. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -15
    gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true
    exit 1
fi

echo "✅ Passo 2 concluído!"
echo ""

# Limpar
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true

# Passo 3: Deploy
echo "🔄 Passo 3: Fazendo deploy do serviço..."
gcloud run deploy monpec \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --allow-unauthenticated \
  --quiet

echo ""
echo "============================================================"
echo "✅ PROCESSO CONCLUÍDO!"
echo "============================================================"
echo ""
echo "🌐 Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
echo ""
