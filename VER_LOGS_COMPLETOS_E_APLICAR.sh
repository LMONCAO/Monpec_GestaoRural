#!/bin/bash
# Ver logs completos e aplicar migrations
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 Verificando logs do job anterior"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-e-verificar" --limit=200 --format="value(textPayload)" 2>/dev/null | grep -v "Container called exit" | tail -80

echo ""
echo "============================================================"
echo "🔧 Aplicando as 56 migrations pendentes"
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

echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute aplicar-56-migrations --region=$REGION --wait

echo ""
echo "📋 Logs do job:"
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-56-migrations" --limit=200 --format="value(textPayload)" 2>/dev/null | grep -v "Container called exit" | tail -50

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations aplicadas!"
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
    echo "❌ Erro. Verifique os logs acima."
fi

gcloud run jobs delete aplicar-56-migrations --region=$REGION --quiet 2>/dev/null || true
