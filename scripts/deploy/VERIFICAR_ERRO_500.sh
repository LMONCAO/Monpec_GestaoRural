#!/bin/bash
# Script para verificar e corrigir erro 500

set -e

echo "=========================================="
echo "🔍 DIAGNÓSTICO ERRO 500"
echo "=========================================="
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
CLOUD_SQL_INSTANCE="monpec-sistema-rural:us-central1:monpec-db"

echo "📋 Verificando logs recentes do erro 500..."
echo "----------------------------------------"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=10 \
    --format="table(timestamp,severity,textPayload)" \
    --project=$PROJECT_ID

echo ""
echo "1️⃣ Verificando conexão Cloud SQL no serviço..."
echo "----------------------------------------"
CLOUD_SQL_CONNECTIONS=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_CONNECTIONS" ]; then
    echo "❌ Conexão Cloud SQL NÃO está configurada no serviço!"
    echo ""
    echo "Adicionando conexão Cloud SQL..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --add-cloudsql-instances=$CLOUD_SQL_INSTANCE \
        --quiet
    
    if [ $? -eq 0 ]; then
        echo "✅ Conexão Cloud SQL adicionada"
    else
        echo "❌ Erro ao adicionar conexão Cloud SQL"
    fi
else
    echo "✅ Conexão Cloud SQL configurada: $CLOUD_SQL_CONNECTIONS"
fi

echo ""
echo "2️⃣ Verificando CLOUD_SQL_CONNECTION_NAME..."
echo "----------------------------------------"
CURRENT_CLOUD_SQL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" 2>/dev/null || echo "")

if [ -z "$CURRENT_CLOUD_SQL" ] || [ "$CURRENT_CLOUD_SQL" != "$CLOUD_SQL_INSTANCE" ]; then
    echo "⚠️ CLOUD_SQL_CONNECTION_NAME não está configurado ou está incorreto"
    echo "   Valor atual: '$CURRENT_CLOUD_SQL'"
    echo "   Valor esperado: '$CLOUD_SQL_INSTANCE'"
    echo ""
    echo "Configurando CLOUD_SQL_CONNECTION_NAME..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_INSTANCE" \
        --quiet
    
    if [ $? -eq 0 ]; then
        echo "✅ CLOUD_SQL_CONNECTION_NAME configurado: $CLOUD_SQL_INSTANCE"
    else
        echo "❌ Erro ao configurar CLOUD_SQL_CONNECTION_NAME"
    fi
else
    echo "✅ CLOUD_SQL_CONNECTION_NAME configurado corretamente: $CURRENT_CLOUD_SQL"
fi

echo ""
echo "3️⃣ Verificando variáveis de ambiente do banco..."
echo "----------------------------------------"
DB_NAME=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_NAME')].value)" 2>/dev/null || echo "")

DB_USER=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_USER')].value)" 2>/dev/null || echo "")

DB_PASSWORD=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_PASSWORD')].value)" 2>/dev/null || echo "")

echo "DB_NAME: ${DB_NAME:-'NÃO CONFIGURADO'}"
echo "DB_USER: ${DB_USER:-'NÃO CONFIGURADO'}"
echo "DB_PASSWORD: ${DB_PASSWORD:+'***CONFIGURADO***'}${DB_PASSWORD:-'NÃO CONFIGURADO'}"

if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo ""
    echo "⚠️ Variáveis do banco de dados não estão todas configuradas!"
    echo "   Configure DB_NAME, DB_USER e DB_PASSWORD se necessário"
fi

echo ""
echo "4️⃣ Verificando instância do Cloud SQL..."
echo "----------------------------------------"
gcloud sql instances describe monpec-db --format="value(connectionName,state)" 2>/dev/null || {
    echo "❌ Instância do Cloud SQL não encontrada ou não acessível"
    echo "   Verifique se a instância 'monpec-db' existe"
}

echo ""
echo "5️⃣ Aguardando atualização do serviço..."
echo "----------------------------------------"
sleep 15

echo ""
echo "6️⃣ Testando acesso ao serviço..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)")

echo "URL: $SERVICE_URL"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço respondendo corretamente (HTTP $HTTP_CODE)"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Erro 500 ainda presente"
    echo ""
    echo "Verificando logs de erro mais recentes..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=5 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -30
elif [ "$HTTP_CODE" = "400" ]; then
    echo "⚠️ Erro 400 ainda presente (ALLOWED_HOSTS)"
else
    echo "⚠️ Serviço retornou HTTP $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "✅ DIAGNÓSTICO CONCLUÍDO"
echo "=========================================="
echo ""
echo "📝 Se o erro 500 persistir, verifique:"
echo "   1. Se o Cloud SQL está acessível"
echo "   2. Se as credenciais do banco estão corretas"
echo "   3. Se as migrações foram aplicadas"
echo "   4. Os logs detalhados acima"
echo ""





