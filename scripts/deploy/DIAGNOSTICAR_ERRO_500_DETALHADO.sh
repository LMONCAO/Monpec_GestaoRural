#!/bin/bash
# Script para diagnosticar erro 500 em detalhes

set -e

echo "=========================================="
echo "🔍 DIAGNÓSTICO DETALHADO - ERRO 500"
echo "=========================================="
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando logs de erro mais recentes..."
echo "----------------------------------------"
echo "Últimos 10 erros:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=10 \
    --format="table(timestamp,severity,textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "2️⃣ Verificando traceback completo..."
echo "----------------------------------------"
echo "Buscando tracebacks completos:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND (severity>=ERROR OR textPayload=~'Traceback')" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | grep -A 50 "Traceback" | head -100

echo ""
echo "3️⃣ Verificando se openpyxl está causando erro..."
echo "----------------------------------------"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND textPayload=~'openpyxl'" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "4️⃣ Verificando erros de importação..."
echo "----------------------------------------"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND (textPayload=~'ModuleNotFoundError' OR textPayload=~'ImportError')" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "5️⃣ Verificando erros de banco de dados..."
echo "----------------------------------------"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND (textPayload=~'OperationalError' OR textPayload=~'database' OR textPayload=~'connection')" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "6️⃣ Verificando revisão mais recente..."
echo "----------------------------------------"
LATEST_REVISION=$(gcloud run revisions list \
    --service=$SERVICE_NAME \
    --region=$REGION \
    --format="value(metadata.name)" \
    --limit=1 \
    --project=$PROJECT_ID)

echo "Revisão: $LATEST_REVISION"
echo ""
echo "Logs específicos desta revisão:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.revision_name=$LATEST_REVISION AND severity>=ERROR" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | head -50

echo ""
echo "=========================================="
echo "✅ DIAGNÓSTICO CONCLUÍDO"
echo "=========================================="
echo ""
echo "📝 Analise os logs acima para identificar o erro específico."
echo ""





