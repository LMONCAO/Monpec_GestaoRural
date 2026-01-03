#!/bin/bash
# Solução ALTERNATIVA para migration duplicada
# Tenta marcar como fake de forma mais direta
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 Primeiro, vamos ver os logs do erro anterior"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -15

echo ""
echo "============================================================"
echo "🔧 SOLUÇÃO ALTERNATIVA: Usar Python direto"
echo "============================================================"
echo ""

# Limpar
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true

# Criar script Python inline que marca a migration como fake
echo "📦 Criando job com script Python inline..."
gcloud run jobs create corrigir-migration \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');call_command('migrate','--noinput')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute corrigir-migration --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations corrigidas!"
    echo ""
    echo "🔄 Fazendo deploy..."
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
    echo "✅ Pronto! Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
else
    echo ""
    echo "❌ Erro. Logs detalhados:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=30 --format="table(timestamp,severity,textPayload)" 2>/dev/null | tail -25
fi

# Limpar
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true
