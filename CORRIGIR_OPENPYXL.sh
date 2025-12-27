#!/bin/bash
# ========================================
# CORRIGIR ERRO openpyxl - REBUILD SEM CACHE
# ========================================

set -e

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec"

gcloud config set project $PROJECT_ID

echo "========================================"
echo "  CORRIGINDO ERRO openpyxl"
echo "========================================"
echo ""

echo "1. Verificando requirements.txt..."
grep -q "openpyxl" requirements.txt && echo "✅ openpyxl está no requirements.txt" || echo "❌ openpyxl NÃO está no requirements.txt"
echo ""

echo "2. Fazendo rebuild SEM CACHE (10-15 min)..."
echo "   Isso força a instalação de TODAS as dependências do zero"
echo ""

# Rebuild sem cache usando cloudbuild.yaml ou diretamente
gcloud builds submit \
    --tag ${IMAGE_NAME}:latest \
    --timeout=30m \
    --no-cache

echo ""
echo "✅ Build concluído"
echo ""

echo "3. Removendo job antigo..."
gcloud run jobs delete migrate-monpec --region $REGION --project $PROJECT_ID --quiet 2>&1 | grep -v "not found" || true
echo ""

echo "4. Criando novo job com imagem corrigida..."
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

echo "5. Executando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --project $PROJECT_ID --wait

echo ""
echo "6. Verificando resultado..."
sleep 5

LATEST_EXECUTION=$(gcloud run jobs executions list --job migrate-monpec --region $REGION --project $PROJECT_ID --limit=1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LATEST_EXECUTION" ]; then
    STATUS=$(gcloud run jobs executions describe $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
    
    if [ "$STATUS" = "True" ]; then
        echo ""
        echo "✅✅✅ SUCESSO! MIGRAÇÕES EXECUTADAS!"
        echo ""
        echo "Seu sistema está pronto:"
        echo "  https://monpec-29862706245.us-central1.run.app"
        echo "  https://monpec-fzzfjppzva-uc.a.run.app"
    else
        echo ""
        echo "⚠️  Status: $STATUS"
        echo ""
        echo "Verificando logs..."
        gcloud alpha run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        gcloud beta run jobs executions logs read $LATEST_EXECUTION --region $REGION --project $PROJECT_ID --limit=100 2>/dev/null || \
        echo "   Ver logs no console: https://console.cloud.google.com/run/jobs/executions/details/us-central1/$LATEST_EXECUTION?project=$PROJECT_ID"
    fi
fi

echo ""
echo "========================================"
echo ""








