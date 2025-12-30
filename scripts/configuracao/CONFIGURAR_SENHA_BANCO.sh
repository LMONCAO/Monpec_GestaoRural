#!/bin/bash
# Script para configurar senha do banco de dados no Cloud Run

set -e

echo "=========================================="
echo "🔐 CONFIGURANDO SENHA DO BANCO DE DADOS"
echo "=========================================="
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_PASSWORD="L6171r12@@jjms"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Configurando DB_PASSWORD no serviço Cloud Run..."
echo "----------------------------------------"

# Verificar se DB_PASSWORD já está configurado
CURRENT_PASSWORD=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_PASSWORD')].value)" 2>/dev/null || echo "")

if [ -n "$CURRENT_PASSWORD" ]; then
    echo "⚠️ DB_PASSWORD já está configurado (será atualizado)"
fi

# Configurar DB_PASSWORD
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --update-env-vars "DB_PASSWORD=$DB_PASSWORD" \
    --quiet

if [ $? -eq 0 ]; then
    echo "✅ DB_PASSWORD configurado com sucesso!"
else
    echo "❌ Erro ao configurar DB_PASSWORD"
    exit 1
fi

echo ""
echo "2️⃣ Verificando outras variáveis do banco..."
echo "----------------------------------------"
DB_NAME=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_NAME')].value)" 2>/dev/null || echo "")

DB_USER=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_USER')].value)" 2>/dev/null || echo "")

echo "DB_NAME: ${DB_NAME:-'NÃO CONFIGURADO (usará padrão: monpec_db)'}"
echo "DB_USER: ${DB_USER:-'NÃO CONFIGURADO (usará padrão: monpec_user)'}"
echo "DB_PASSWORD: ✅ CONFIGURADO"

# Configurar DB_NAME e DB_USER se não estiverem configurados
if [ -z "$DB_NAME" ]; then
    echo ""
    echo "Configurando DB_NAME..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "DB_NAME=monpec_db" \
        --quiet
    echo "✅ DB_NAME configurado: monpec_db"
fi

if [ -z "$DB_USER" ]; then
    echo ""
    echo "Configurando DB_USER..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "DB_USER=monpec_user" \
        --quiet
    echo "✅ DB_USER configurado: monpec_user"
fi

echo ""
echo "3️⃣ Verificando CLOUD_SQL_CONNECTION_NAME..."
echo "----------------------------------------"
CLOUD_SQL_CONN=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_CONN" ]; then
    echo "⚠️ CLOUD_SQL_CONNECTION_NAME não configurado. Configurando..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
        --quiet
    echo "✅ CLOUD_SQL_CONNECTION_NAME configurado"
else
    echo "✅ CLOUD_SQL_CONNECTION_NAME já está configurado: $CLOUD_SQL_CONN"
fi

echo ""
echo "4️⃣ Verificando conexão Cloud SQL no serviço..."
echo "----------------------------------------"
CLOUD_SQL_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_INSTANCES" ]; then
    echo "⚠️ Conexão Cloud SQL não está configurada. Adicionando..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
        --quiet
    echo "✅ Conexão Cloud SQL adicionada"
else
    echo "✅ Conexão Cloud SQL já está configurada: $CLOUD_SQL_INSTANCES"
fi

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
echo "Fazendo requisição de teste..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" || echo "000")
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço respondendo corretamente!"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "⚠️ Erro 500 ainda presente"
    echo ""
    echo "Verificando logs de erro..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -30
else
    echo "⚠️ Serviço retornou HTTP $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "✅ CONFIGURAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "📝 Resumo:"
echo "  - DB_PASSWORD: ✅ Configurado"
echo "  - DB_NAME: ${DB_NAME:-'monpec_db (padrão)'}"
echo "  - DB_USER: ${DB_USER:-'monpec_user (padrão)'}"
echo "  - CLOUD_SQL_CONNECTION_NAME: ${CLOUD_SQL_CONN:-'monpec-sistema-rural:us-central1:monpec-db'}"
echo "  - Conexão Cloud SQL: $([ -n "$CLOUD_SQL_INSTANCES" ] && echo "✅ Configurada" || echo "✅ Adicionada")"
echo ""
echo "🔗 URL do serviço: $SERVICE_URL"
echo ""





