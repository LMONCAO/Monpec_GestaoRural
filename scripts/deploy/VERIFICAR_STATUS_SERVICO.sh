#!/bin/bash
# Script para verificar status do serviço após configuração da senha

set -e

echo "=========================================="
echo "🔍 VERIFICANDO STATUS DO SERVIÇO"
echo "=========================================="
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando variáveis de ambiente do banco..."
echo "----------------------------------------"
DB_PASSWORD=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_PASSWORD')].value)" 2>/dev/null || echo "")

DB_NAME=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_NAME')].value)" 2>/dev/null || echo "")

DB_USER=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_USER')].value)" 2>/dev/null || echo "")

CLOUD_SQL_CONN=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" 2>/dev/null || echo "")

echo "DB_PASSWORD: ${DB_PASSWORD:+'✅ CONFIGURADO'}${DB_PASSWORD:-'❌ NÃO CONFIGURADO'}"
echo "DB_NAME: ${DB_NAME:-'monpec_db (padrão)'}"
echo "DB_USER: ${DB_USER:-'monpec_user (padrão)'}"
echo "CLOUD_SQL_CONNECTION_NAME: ${CLOUD_SQL_CONN:-'❌ NÃO CONFIGURADO'}"

echo ""
echo "2️⃣ Verificando conexão Cloud SQL..."
echo "----------------------------------------"
CLOUD_SQL_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if [ -n "$CLOUD_SQL_INSTANCES" ]; then
    echo "✅ Conexão Cloud SQL configurada: $CLOUD_SQL_INSTANCES"
else
    echo "❌ Conexão Cloud SQL NÃO configurada"
fi

echo ""
echo "3️⃣ Verificando status do serviço..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)")

SERVICE_STATUS=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.conditions[0].status)")

echo "URL: $SERVICE_URL"
echo "Status: $SERVICE_STATUS"

echo ""
echo "4️⃣ Testando acesso ao serviço..."
echo "----------------------------------------"
echo "Fazendo requisição HTTP..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")

echo "HTTP Status Code: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Serviço funcionando corretamente! (HTTP 200)"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço redirecionando (HTTP $HTTP_CODE) - Normal"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Erro 500 - Internal Server Error"
    echo ""
    echo "Verificando logs de erro mais recentes..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -40
elif [ "$HTTP_CODE" = "400" ]; then
    echo "❌ Erro 400 - Bad Request (ALLOWED_HOSTS)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "⚠️ Não foi possível conectar ao serviço"
else
    echo "⚠️ Serviço retornou HTTP $HTTP_CODE"
fi

echo ""
echo "5️⃣ Verificando revisão mais recente..."
echo "----------------------------------------"
LATEST_REVISION=$(gcloud run revisions list \
    --service=$SERVICE_NAME \
    --region=$REGION \
    --format="value(metadata.name)" \
    --limit=1)

echo "Revisão mais recente: $LATEST_REVISION"

echo ""
echo "=========================================="
echo "✅ VERIFICAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "📝 Resumo:"
echo "  - DB_PASSWORD: $([ -n "$DB_PASSWORD" ] && echo "✅ Configurado" || echo "❌ Não configurado")"
echo "  - Conexão Cloud SQL: $([ -n "$CLOUD_SQL_INSTANCES" ] && echo "✅ Configurada" || echo "❌ Não configurada")"
echo "  - Status HTTP: $HTTP_CODE"
echo ""
echo "🔗 URL do serviço: $SERVICE_URL"
echo ""





