#!/bin/bash
# Aplicar as 56 migrations pendentes (0035 até 0089)
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔧 Aplicando 56 migrations pendentes (0035 até 0089)"
echo "============================================================"
echo ""

gcloud run jobs delete aplicar-56-migrations --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-56-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando (aguarde 3-5 minutos para aplicar 56 migrations)..."
gcloud run jobs execute aplicar-56-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations aplicadas!"
    echo ""
    echo "📋 Verificando estado final..."
    gcloud run jobs create verificar-final \
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
    
    gcloud run jobs execute verificar-final --region=$REGION --wait
    echo ""
    echo "📊 Logs da verificação:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-final" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[X\]|\[ \]|gestao_rural" | tail -20
    
    gcloud run jobs delete verificar-final --region=$REGION --quiet 2>/dev/null || true
    
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
    echo "❌ Erro ao aplicar migrations. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-56-migrations" --limit=50 --format="value(textPayload)" 2>/dev/null | tail -30
fi

gcloud run jobs delete aplicar-56-migrations --region=$REGION --quiet 2>/dev/null || true
