#!/bin/bash
# Aplicar migrations marcando 0034, 0035 e 0036 como fake
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Aplicando migrations (marcando 0034, 0035 e 0036 como fake)..."
gcloud run jobs delete aplicar-mig-0034-0035-0036 --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-mig-0034-0035-0036 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;print('Marcando 0034 como fake...');call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');print('Marcando 0035 como fake...');call_command('migrate','gestao_rural','0035_assinaturas_stripe','--fake');print('Marcando 0036 como fake...');call_command('migrate','gestao_rural','0036_ajusteorcamentocompra_orcamentocompramensal_and_more','--fake');print('Aplicando migrations restantes...');call_command('migrate','--noinput');print('✅ Concluído!')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute aplicar-mig-0034-0035-0036 --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations aplicadas!"
    echo ""
    echo "📋 Verificando estado final..."
    gcloud run jobs delete verificar-final-mig --region=$REGION --quiet 2>/dev/null || true
    
    gcloud run jobs create verificar-final-mig \
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
    
    gcloud run jobs execute verificar-final-mig --region=$REGION --wait
    
    PENDENTES=$(gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-final-mig" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | wc -l)
    echo ""
    echo "   Migrations pendentes: $PENDENTES"
    
    if [ "$PENDENTES" -gt 0 ]; then
        echo ""
        echo "📋 Primeiras 10 migrations pendentes:"
        gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-final-mig" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | head -10
    fi
    
    gcloud run jobs delete verificar-final-mig --region=$REGION --quiet 2>/dev/null || true
else
    echo ""
    echo "❌ Erro. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-mig-0034-0035-0036" --limit=50 --format="value(textPayload)" 2>/dev/null | tail -30
fi

gcloud run jobs delete aplicar-mig-0034-0035-0036 --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "✅ Processo concluído!"

