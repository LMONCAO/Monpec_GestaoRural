#!/bin/bash
# Script CORRIGIDO para diagnosticar e corrigir erro 500
# Execute no Google Cloud Shell

echo "============================================================"
echo "🔧 CORRIGIR ERRO 500 - SISTEMA MONPEC (VERSÃO CORRIGIDA)"
echo "============================================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

# Configurar projeto
gcloud config set project $PROJECT_ID

echo "1️⃣ Verificando logs de erro do serviço..."
echo ""
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=5 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -10

echo ""
echo "2️⃣ Verificando status do Cloud SQL..."
SQL_STATUS=$(gcloud sql instances describe $DB_INSTANCE --format="value(state)" 2>/dev/null)
if [ "$SQL_STATUS" = "RUNNABLE" ]; then
    echo "   ✅ Cloud SQL está rodando"
else
    echo "   ⚠️ Cloud SQL status: $SQL_STATUS"
    echo "   💡 Se não estiver rodando, execute: gcloud sql instances patch $DB_INSTANCE --activation-policy=ALWAYS"
fi

echo ""
echo "3️⃣ Verificando logs do job que falhou anteriormente..."
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500 AND severity>=ERROR" --limit=10 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -15

echo ""
echo "4️⃣ Aplicando migrations (versão simplificada)..."
echo "   ⏱️  Isso pode levar 2-4 minutos..."
echo ""

# Deletar job anterior se existir
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

# Criar job simplificado para aplicar migrations
echo "   📦 Criando job..."
gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=600

if [ $? -ne 0 ]; then
    echo "   ❌ ERRO: Não foi possível criar o job."
    echo "   💡 Verifique se a imagem existe: gcloud container images list --repository=gcr.io/$PROJECT_ID"
    exit 1
fi

echo "   ✅ Job criado! Executando..."
echo "   ⏱️  Aguarde 2-4 minutos..."
echo ""

# Executar o job e mostrar output
gcloud run jobs execute corrigir-500 --region=$REGION --wait

EXECUTION_STATUS=$?

if [ $EXECUTION_STATUS -eq 0 ]; then
    echo ""
    echo "   ✅ Migrations aplicadas com sucesso!"
else
    echo ""
    echo "   ⚠️ Job falhou. Verificando logs..."
    echo ""
    # Ver logs do job
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-500" --limit=20 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -25
    echo ""
    echo "   💡 Verifique os logs acima para entender o erro"
fi

# Limpar job
echo ""
echo "🧹 Limpando job temporário..."
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "5️⃣ Verificando logs do serviço para entender o erro 500..."
echo ""
echo "   Últimos erros do serviço:"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=10 --format="value(textPayload)" 2>/dev/null | head -5

echo ""
echo "6️⃣ Reiniciando serviço (forçando novo deploy)..."
gcloud run services update $SERVICE_NAME --region=$REGION --update-env-vars="RESTART=$(date +%s)" --quiet

if [ $? -eq 0 ]; then
    echo "   ✅ Serviço atualizado"
else
    echo "   ⚠️ Não foi possível atualizar serviço"
fi

echo ""
echo "============================================================"
echo "✅ Processo concluído!"
echo "============================================================"
echo ""
echo "🌐 Teste o sistema em:"
echo "   https://monpec-fzzfjppzva-uc.a.run.app/login/"
echo ""
echo "💡 Se ainda houver erro 500:"
echo ""
echo "   1. Veja os logs detalhados do serviço:"
echo "      gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=50"
echo ""
echo "   2. Habilite DEBUG temporariamente (apenas para diagnóstico):"
echo "      gcloud run services update $SERVICE_NAME --region=$REGION --update-env-vars=\"DEBUG=True\""
echo "      (Depois desabilite: DEBUG=False)"
echo ""
echo "   3. Verifique se o banco está acessível:"
echo "      gcloud sql instances describe $DB_INSTANCE"
echo ""
