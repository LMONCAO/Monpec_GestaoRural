#!/bin/bash
# Comando SIMPLES para aplicar as 57 migrations pendentes
# Copie TODO e cole no Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "🔧 Aplicando 57 migrations pendentes..."
echo "⏱️  Isso pode levar 3-5 minutos..."
echo ""

# Limpar job anterior
gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>/dev/null || true

# Criar e executar job
gcloud run jobs create aplicar-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "Executando..."
gcloud run jobs execute aplicar-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations aplicadas!"
    echo ""
    echo "🔄 Agora fazendo deploy do serviço..."
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
    echo "❌ Erro. Ver logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migrations" --limit=20
fi

# Limpar
gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>/dev/null || true
