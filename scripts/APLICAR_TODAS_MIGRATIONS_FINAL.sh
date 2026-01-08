#!/bin/bash
# Aplicar TODAS as migrations (incluindo marcar 0034 como fake primeiro)
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔧 APLICANDO TODAS AS MIGRATIONS"
echo "============================================================"
echo ""
echo "Problema: 56 migrations não aplicadas"
echo "Solução: Marcar 0034 como fake e aplicar todas"
echo ""

# Limpar
gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>/dev/null || true

echo "📦 Criando job para aplicar todas as migrations..."
gcloud run jobs create aplicar-todas-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;print('Marcando 0034 como fake...');call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');print('Aplicando todas as migrations...');call_command('migrate','--noinput');print('✅ Todas as migrations aplicadas!')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute aplicar-todas-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Todas as migrations aplicadas!"
    echo ""
    echo "📋 Verificando estado das migrations..."
    gcloud run jobs create verificar-migrations \
      --region=$REGION \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="python" \
      --args="manage.py,showmigrations,--list" \
      --max-retries=1 \
      --memory=2Gi \
      --cpu=2 \
      --task-timeout=300
    
    gcloud run jobs execute verificar-migrations --region=$REGION --wait
    gcloud run jobs delete verificar-migrations --region=$REGION --quiet 2>/dev/null || true
    
    echo ""
    echo "🔄 Fazendo deploy do serviço..."
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
    echo "❌ Erro. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-todas-migrations" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
fi

# Limpar
gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>/dev/null || true
