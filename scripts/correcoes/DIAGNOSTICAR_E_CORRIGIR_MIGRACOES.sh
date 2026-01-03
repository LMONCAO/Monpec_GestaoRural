#!/bin/bash
# ========================================
# DIAGNOSTICAR E CORRIGIR MIGRAÇÕES
# ========================================

set -e

PROJECT_ID="monpec-sistema-rural"
JOB_NAME="migrate-monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec"

# Configurar projeto
gcloud config set project $PROJECT_ID > /dev/null 2>&1

echo "========================================"
echo "  DIAGNOSTICANDO ERRO DAS MIGRAÇÕES"
echo "========================================"
echo ""

# 1. Listar execuções recentes para ver o erro
echo "1. Buscando execuções recentes do job..."
EXECUTIONS=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null || echo "")

if [ -n "$EXECUTIONS" ]; then
    EXECUTION_NAME=$(echo $EXECUTIONS | head -1)
    echo "   Execução encontrada: $EXECUTION_NAME"
    echo ""
    
    echo "2. Verificando detalhes do erro..."
    gcloud run jobs executions describe $EXECUTION_NAME --region $REGION --project $PROJECT_ID --format="yaml(status)" | head -30
    echo ""
    
    echo "3. Verificando logs do erro..."
    gcloud alpha run jobs executions logs read $EXECUTION_NAME --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
    gcloud beta run jobs executions logs read $EXECUTION_NAME --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
    echo "   (Logs não disponíveis nesta versão do gcloud)"
    echo ""
else
    echo "   Nenhuma execução encontrada. O job pode não ter sido criado corretamente."
    echo ""
fi

echo "========================================"
echo "  CORRIGINDO O PROBLEMA"
echo "========================================"
echo ""

# 2. Deletar job antigo
echo "4. Removendo job antigo..."
gcloud run jobs delete $JOB_NAME --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true
echo "✅ Job removido"
echo ""

# 3. Criar job com configuração corrigida
echo "5. Criando job corrigido..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

gcloud run jobs create $JOB_NAME \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --project $PROJECT_ID \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600 \
    --memory=2Gi \
    --cpu=2 \
    --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

echo "✅ Job criado"
echo ""

# 4. Executar migrações
echo "6. Executando migrações..."
gcloud run jobs execute $JOB_NAME --region $REGION --project $PROJECT_ID --wait
echo ""

# 5. Verificar resultado
echo "7. Verificando resultado..."
sleep 5
EXECUTION_STATUS=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")

if [ "$EXECUTION_STATUS" = "True" ]; then
    echo "✅✅✅ MIGRAÇÕES EXECUTADAS COM SUCESSO!"
    echo ""
    echo "Seu sistema está pronto! Teste agora:"
    echo "  https://monpec-29862706245.us-central1.run.app"
    echo "  https://monpec-fzzfjppzva-uc.a.run.app"
else
    echo "⚠️  Status: $EXECUTION_STATUS"
    echo ""
    echo "Verificando logs detalhados..."
    LATEST_EXECUTION=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)
    if [ -n "$LATEST_EXECUTION" ]; then
        gcloud alpha run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        gcloud beta run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        echo "   (Logs não disponíveis)"
    fi
fi

echo ""
echo "========================================"
echo ""


