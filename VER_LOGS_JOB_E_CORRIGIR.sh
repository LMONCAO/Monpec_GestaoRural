#!/bin/bash
# Ver logs do job que falhou e corrigir
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 LOGS DO JOB QUE FALHOU"
echo "============================================================"
echo ""

# Ver logs do último job
EXECUTION_NAME=$(gcloud run jobs executions list --job=corrigir-500 --region=$REGION --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$EXECUTION_NAME" ]; then
    echo "📊 Logs da execução: $EXECUTION_NAME"
    echo ""
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=50 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -30
else
    echo "⚠️ Nenhuma execução encontrada"
fi

echo ""
echo "============================================================"
echo "🔧 APLICANDO MIGRATIONS (VERSÃO ROBUSTA)"
echo "============================================================"
echo ""

# Deletar job anterior
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

echo "📦 Criando job com configuração melhorada..."
gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && echo '=== Verificando conexão com banco ===' && python -c 'import os; os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"sistema_rural.settings_gcp\"); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\"SELECT 1\"); print(\"✅ Conexão OK\")' && echo '=== Aplicando migrations ===' && python manage.py migrate --noinput && echo '=== Verificando migrations aplicadas ===' && python manage.py showmigrations --list | tail -5" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

if [ $? -ne 0 ]; then
    echo "❌ ERRO ao criar job"
    exit 1
fi

echo ""
echo "⏱️  Executando job (aguarde 3-5 minutos)..."
echo ""

gcloud run jobs execute corrigir-500 --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations aplicadas com sucesso!"
    echo ""
    echo "📋 Últimos logs do job:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=10 --format="value(textPayload)" 2>/dev/null | tail -5
else
    echo ""
    echo "❌ Job falhou. Verificando logs..."
    echo ""
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=20 --format="table(timestamp,severity,textPayload)" 2>/dev/null | tail -15
    exit 1
fi

# Limpar
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "============================================================"
echo "🔄 REINICIANDO SERVIÇO"
echo "============================================================"
echo ""

# Não usar --update-env-vars com RESTART, isso pode causar problemas
# Em vez disso, fazer um deploy simples que força nova revisão
echo "📦 Fazendo deploy para forçar nova revisão..."
gcloud run deploy $SERVICE_NAME \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --add-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --allow-unauthenticated \
  --quiet

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Serviço atualizado!"
else
    echo ""
    echo "⚠️ Houve problemas no deploy. Verifique os logs."
fi

echo ""
echo "============================================================"
echo "✅ PROCESSO CONCLUÍDO!"
echo "============================================================"
echo ""
echo "🌐 Teste o sistema em:"
echo "   https://monpec-fzzfjppzva-uc.a.run.app/login/"
echo ""
echo "💡 Se ainda houver erro, verifique os logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=20"
echo ""
