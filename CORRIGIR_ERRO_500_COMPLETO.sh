#!/bin/bash
# Script completo para diagnosticar e corrigir erro 500
# Execute no Google Cloud Shell

echo "============================================================"
echo "🔧 CORRIGIR ERRO 500 - SISTEMA MONPEC"
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

echo "1️⃣ Verificando status do serviço..."
SERVICE_STATUS=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.conditions[0].status)" 2>/dev/null)
if [ "$SERVICE_STATUS" = "True" ]; then
    echo "   ✅ Serviço está rodando"
else
    echo "   ⚠️ Serviço pode ter problemas"
fi

echo ""
echo "2️⃣ Verificando últimos erros nos logs..."
echo "   (Mostrando últimos 10 erros)"
echo ""
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=10 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -15

echo ""
echo "3️⃣ Verificando Cloud SQL..."
SQL_STATUS=$(gcloud sql instances describe $DB_INSTANCE --format="value(state)" 2>/dev/null)
if [ "$SQL_STATUS" = "RUNNABLE" ]; then
    echo "   ✅ Cloud SQL está rodando"
else
    echo "   ⚠️ Cloud SQL status: $SQL_STATUS"
fi

echo ""
echo "4️⃣ Aplicando migrations pendentes..."
echo "   ⏱️  Isso pode levar 1-3 minutos..."
echo ""

# Deletar job anterior se existir
gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true

# Criar job para aplicar migrations
gcloud run jobs create corrigir-500 \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && echo 'Verificando migrations...' && python manage.py showmigrations --list | grep '\[ \]' && echo 'Aplicando migrations...' && python manage.py migrate --noinput && echo '✅ Migrations aplicadas!' || echo '✅ Nenhuma migration pendente'" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "   📦 Job criado, executando..."
    gcloud run jobs execute corrigir-500 --region=$REGION --wait > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Migrations verificadas/aplicadas"
    else
        echo "   ⚠️ Houve problemas ao executar migrations (verifique logs)"
    fi
    
    # Limpar job
    gcloud run jobs delete corrigir-500 --region=$REGION --quiet 2>/dev/null || true
else
    echo "   ⚠️ Não foi possível criar job (pode ser problema de imagem)"
fi

echo ""
echo "5️⃣ Reiniciando serviço..."
# Forçar novo deploy para reiniciar o serviço
gcloud run services update $SERVICE_NAME --region=$REGION --update-env-vars="RESTART=$(date +%s)" --quiet 2>/dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ Serviço reiniciado"
else
    echo "   ⚠️ Não foi possível reiniciar serviço (tente manualmente)"
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
echo "   1. Verifique os logs detalhados:"
echo "      gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=50"
echo ""
echo "   2. Verifique se o banco está acessível:"
echo "      gcloud sql instances describe $DB_INSTANCE"
echo ""
echo "   3. Tente habilitar DEBUG temporariamente (apenas para diagnóstico):"
echo "      gcloud run services update $SERVICE_NAME --region=$REGION --update-env-vars=\"DEBUG=True\""
echo ""
