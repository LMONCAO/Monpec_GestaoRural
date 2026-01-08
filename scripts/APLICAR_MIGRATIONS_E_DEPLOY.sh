#!/bin/bash
# Aplicar migrations e fazer deploy (solução completa)
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔧 PASSO 1: Aplicar todas as migrations novamente"
echo "============================================================"
echo ""

gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-todas-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;print('Marcando 0034 como fake...');call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');print('Aplicando todas as migrations...');call_command('migrate','--noinput');print('Verificando...');call_command('showmigrations','--list')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute aplicar-todas-migrations --region=$REGION --wait

echo ""
echo "📋 Logs do job:"
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-todas-migrations" --limit=50 --format="value(textPayload)" 2>/dev/null | tail -30

gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "============================================================"
echo "🔄 PASSO 2: Fazendo deploy do serviço"
echo "============================================================"
echo ""

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
  --port=8080

echo ""
echo "✅ Processo concluído!"
echo "🌐 Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
