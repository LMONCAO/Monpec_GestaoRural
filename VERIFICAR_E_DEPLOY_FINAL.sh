#!/bin/bash
# Verificar estado final e fazer deploy
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📊 Verificando estado final das migrations"
echo "============================================================"
echo ""

gcloud run jobs delete verificar-final-estado --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create verificar-final-estado \
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

gcloud run jobs execute verificar-final-estado --region=$REGION --wait

PENDENTES=$(gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-final-estado" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | wc -l)
echo ""
echo "   Migrations pendentes: $PENDENTES"

if [ "$PENDENTES" -eq 0 ]; then
    echo ""
    echo "✅ Todas as migrations estão aplicadas!"
else
    echo ""
    echo "📋 Primeiras 10 migrations pendentes:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-final-estado" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | head -10
fi

gcloud run jobs delete verificar-final-estado --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "============================================================"
echo "🔄 Fazendo deploy do serviço"
echo "============================================================"
echo ""

gcloud run deploy monpec \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --allow-unauthenticated \
  --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
    echo "============================================================"
    echo ""
    echo "⏱️  Aguarde 1-2 minutos para o serviço inicializar..."
    echo ""
    echo "🌐 Teste o sistema em:"
    echo "   https://monpec-fzzfjppzva-uc.a.run.app/login/"
    echo ""
    echo "💡 Se ainda houver erro 500, verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=monpec\" --limit=5 --format=\"value(textPayload)\""
else
    echo ""
    echo "❌ Deploy falhou. Verifique os logs acima."
fi


