#!/bin/bash
# Script para corrigir project ID e verificar erro 500

set -e

echo "=========================================="
echo "🔧 CORRIGINDO E VERIFICANDO ERRO 500"
echo "=========================================="
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "1️⃣ Corrigindo project ID..."
echo "----------------------------------------"
gcloud config set project $PROJECT_ID

# Verificar se foi configurado corretamente
CURRENT_PROJECT=$(gcloud config get-value project)
echo "Project atual: $CURRENT_PROJECT"

if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "❌ Erro ao configurar project. Tentando novamente..."
    gcloud config unset project
    gcloud config set project $PROJECT_ID
fi

echo ""
echo "2️⃣ Verificando logs de erro mais recentes..."
echo "----------------------------------------"
echo "Últimos 5 erros:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | head -50

echo ""
echo "3️⃣ Verificando variáveis de ambiente críticas..."
echo "----------------------------------------"
echo "DB_PASSWORD:"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_PASSWORD')].value)" \
    --project=$PROJECT_ID 2>/dev/null || echo "NÃO CONFIGURADO"

echo ""
echo "CLOUD_SQL_CONNECTION_NAME:"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" \
    --project=$PROJECT_ID 2>/dev/null || echo "NÃO CONFIGURADO"

echo ""
echo "4️⃣ Verificando conexão Cloud SQL..."
echo "----------------------------------------"
CLOUD_SQL_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" \
    --project=$PROJECT_ID 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_INSTANCES" ]; then
    echo "❌ Conexão Cloud SQL NÃO configurada"
    echo "Adicionando conexão..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
        --project=$PROJECT_ID \
        --quiet
    echo "✅ Conexão Cloud SQL adicionada"
else
    echo "✅ Conexão Cloud SQL: $CLOUD_SQL_INSTANCES"
fi

echo ""
echo "5️⃣ Verificando se DB_PASSWORD está configurado..."
echo "----------------------------------------"
DB_PASSWORD=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_PASSWORD')].value)" \
    --project=$PROJECT_ID 2>/dev/null || echo "")

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ DB_PASSWORD NÃO está configurado!"
    echo ""
    echo "Configurando DB_PASSWORD..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "DB_PASSWORD=L6171r12@@jjms" \
        --project=$PROJECT_ID \
        --quiet
    echo "✅ DB_PASSWORD configurado"
else
    echo "✅ DB_PASSWORD já está configurado"
fi

echo ""
echo "6️⃣ Verificando CLOUD_SQL_CONNECTION_NAME..."
echo "----------------------------------------"
CLOUD_SQL_CONN=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" \
    --project=$PROJECT_ID 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_CONN" ]; then
    echo "⚠️ CLOUD_SQL_CONNECTION_NAME não configurado. Configurando..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
        --project=$PROJECT_ID \
        --quiet
    echo "✅ CLOUD_SQL_CONNECTION_NAME configurado"
else
    echo "✅ CLOUD_SQL_CONNECTION_NAME: $CLOUD_SQL_CONN"
fi

echo ""
echo "7️⃣ Aguardando atualização do serviço..."
echo "----------------------------------------"
sleep 20

echo ""
echo "8️⃣ Testando acesso ao serviço..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)" \
    --project=$PROJECT_ID)

echo "URL: $SERVICE_URL"
echo "Fazendo requisição de teste..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço funcionando corretamente!"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Erro 500 ainda presente"
    echo ""
    echo "Verificando logs de erro detalhados..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -50
    echo ""
    echo "💡 Possíveis causas:"
    echo "   1. Senha do banco incorreta"
    echo "   2. Banco de dados não existe"
    echo "   3. Usuário do banco não tem permissões"
    echo "   4. Migrações não aplicadas"
else
    echo "⚠️ Serviço retornou HTTP $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "✅ VERIFICAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "🔗 URL: $SERVICE_URL"
echo ""





