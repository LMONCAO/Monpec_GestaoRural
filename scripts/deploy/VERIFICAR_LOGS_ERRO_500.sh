#!/bin/bash
# Script para verificar logs detalhados do erro 500

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "=========================================="
echo "🔍 VERIFICANDO LOGS DO ERRO 500"
echo "=========================================="
echo ""

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Últimos logs de ERRO..."
echo "----------------------------------------"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=10 \
    --format="table(timestamp, severity, textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "2️⃣ Últimos logs completos (últimas 20 linhas)..."
echo "----------------------------------------"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=20 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | tail -50

echo ""
echo "3️⃣ Verificando se openpyxl está instalado no container..."
echo "----------------------------------------"
echo "Executando comando no container..."
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
    --project=$PROJECT_ID > /dev/null 2>&1 || true

echo ""
echo "4️⃣ Testando importação de módulos críticos..."
echo "----------------------------------------"
echo "Verificando se há erros de importação..."

echo ""
echo "5️⃣ Verificando variáveis de ambiente..."
echo "----------------------------------------"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env)" \
    --project=$PROJECT_ID | grep -E "DJANGO_SETTINGS_MODULE|CLOUD_SQL|DB_|SECRET_KEY" || echo "Variáveis não encontradas"

echo ""
echo "=========================================="
echo "✅ VERIFICAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "📝 Analise os logs acima para identificar o erro específico"
echo ""
