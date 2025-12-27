#!/bin/bash
# ========================================
# REBUILD SEM CACHE - FORÇAR INSTALAÇÃO DE TODAS AS DEPENDÊNCIAS
# ========================================

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

gcloud config set project $PROJECT_ID

echo "========================================"
echo "  REBUILD SEM CACHE - CORRIGIR openpyxl"
echo "========================================"
echo ""

echo "1. Verificando requirements.txt..."
if grep -q "openpyxl" requirements.txt; then
    echo "✅ openpyxl encontrado no requirements.txt"
    grep "openpyxl" requirements.txt
else
    echo "❌ openpyxl NÃO encontrado! Adicionando..."
    echo "openpyxl>=3.1.5" >> requirements.txt
fi
echo ""

echo "2. Fazendo rebuild SEM CACHE (pode levar 10-15 minutos)..."
echo "   Isso garante que todas as dependências sejam instaladas do zero"
echo ""

gcloud builds submit \
    --tag ${IMAGE_NAME}:latest \
    --timeout=30m \
    --no-cache \
    --substitutions=_DOCKERFILE=Dockerfile.prod

echo ""
echo "✅ Build concluído sem cache"
echo ""

echo "3. Verificando se openpyxl foi instalado na imagem..."
echo "   (Criando job de teste para verificar)"
echo ""

# Criar job temporário para verificar
gcloud run jobs create test-openpyxl \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --project $PROJECT_ID \
    --command python \
    --args -c,"import openpyxl; print('openpyxl versão:', openpyxl.__version__)" \
    --max-retries 1 \
    --task-timeout 60 \
    --memory=512Mi \
    --cpu=1 \
    --quiet 2>&1 | grep -v "already" || true

echo "   Executando teste..."
gcloud run jobs execute test-openpyxl --region $REGION --project $PROJECT_ID --wait 2>&1 | tail -10

# Limpar job de teste
gcloud run jobs delete test-openpyxl --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true

echo ""
echo "4. Atualizando serviço Cloud Run com nova imagem..."
gcloud run services update $SERVICE_NAME \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --project $PROJECT_ID \
    --quiet

echo ""
echo "5. Removendo job de migração antigo..."
gcloud run jobs delete migrate-monpec --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true

echo ""
echo "6. Criando novo job de migração..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

gcloud run jobs create migrate-monpec \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --project $PROJECT_ID \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 1 \
    --task-timeout 900 \
    --memory=2Gi \
    --cpu=2 \
    --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

echo "✅ Job criado"
echo ""

echo "7. Executando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --project $PROJECT_ID --wait

echo ""
echo "8. Verificando resultado..."
sleep 5

LATEST_EXECUTION=$(gcloud run jobs executions list --job migrate-monpec --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LATEST_EXECUTION" ]; then
    STATUS=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
    
    if [ "$STATUS" = "True" ]; then
        echo ""
        echo "✅✅✅ MIGRAÇÕES EXECUTADAS COM SUCESSO!"
        echo ""
        echo "Seu sistema está pronto! Teste agora:"
        echo "  https://monpec-29862706245.us-central1.run.app"
        echo "  https://monpec-fzzfjppzva-uc.a.run.app"
    else
        echo ""
        echo "❌ Execução falhou"
        echo "   Verificando logs..."
        echo ""
        gcloud alpha run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=50 2>/dev/null || \
        gcloud beta run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=50 2>/dev/null || \
        echo "   Execute no console para ver logs completos"
    fi
fi

echo ""
echo "========================================"
echo ""








