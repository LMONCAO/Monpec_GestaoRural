#!/bin/bash
# Corrigir migration duplicada - tabela já existe mas migration não está registrada
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔧 CORRIGINDO MIGRATION DUPLICADA"
echo "============================================================"
echo ""
echo "Problema: Tabela 'gestao_rural_contafinanceira' já existe"
echo "Solução: Marcar migration como aplicada sem executá-la (--fake)"
echo ""

# Limpar job anterior
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true

echo "📦 Criando job para corrigir migration..."
gcloud run jobs create corrigir-migration \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,cd /app && echo 'Marcando migration 0034 como aplicada (fake)...' && python manage.py migrate gestao_rural 0034_financeiro_reestruturado --fake && echo 'Aplicando migrations restantes...' && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo ""
echo "⏱️  Executando (aguarde 3-5 minutos)..."
gcloud run jobs execute corrigir-migration --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration corrigida!"
    echo ""
    echo "📋 Verificando migrations aplicadas..."
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
    echo "❌ Erro. Ver logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
fi

# Limpar
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true
