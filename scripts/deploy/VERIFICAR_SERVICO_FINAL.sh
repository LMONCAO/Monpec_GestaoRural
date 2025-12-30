#!/bin/bash
# Script para verificar se o serviço está funcionando após o deploy

set -e

echo "=========================================="
echo "🔍 VERIFICANDO SERVIÇO APÓS DEPLOY"
echo "=========================================="
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando status do serviço..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)" \
    --project=$PROJECT_ID)

LATEST_REVISION=$(gcloud run revisions list \
    --service=$SERVICE_NAME \
    --region=$REGION \
    --format="value(metadata.name)" \
    --limit=1 \
    --project=$PROJECT_ID)

echo "URL: $SERVICE_URL"
echo "Revisão mais recente: $LATEST_REVISION"
echo "Status:"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="table(status.conditions[0].type,status.conditions[0].status)" \
    --project=$PROJECT_ID

echo ""
echo "2️⃣ Testando acesso HTTP..."
echo "----------------------------------------"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")
HTTP_BODY=$(curl -s "$SERVICE_URL" | head -c 200)

echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Serviço funcionando perfeitamente! (HTTP 200)"
    echo ""
    echo "Primeiros 200 caracteres da resposta:"
    echo "$HTTP_BODY"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço redirecionando (HTTP $HTTP_CODE) - Normal"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Erro 500 ainda presente"
    echo ""
    echo "3️⃣ Verificando logs de erro..."
    echo "----------------------------------------"
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=5 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -50
elif [ "$HTTP_CODE" = "400" ]; then
    echo "❌ Erro 400 - Bad Request (ALLOWED_HOSTS)"
    echo "   O middleware pode não estar funcionando corretamente"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "⚠️ Não foi possível conectar ao serviço"
else
    echo "⚠️ Serviço retornou HTTP $HTTP_CODE"
fi

echo ""
echo "4️⃣ Verificando variáveis de ambiente..."
echo "----------------------------------------"
echo "Variáveis críticas:"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="table(spec.template.spec.containers[0].env.name,spec.template.spec.containers[0].env.value)" \
    --project=$PROJECT_ID | grep -E "(DJANGO_SETTINGS_MODULE|DEBUG|CLOUD_SQL|DB_|SECRET_KEY)" || echo "Nenhuma variável relevante encontrada"

echo ""
echo "5️⃣ Verificando conexão Cloud SQL..."
echo "----------------------------------------"
CLOUD_SQL_INSTANCES=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" \
    --project=$PROJECT_ID)

if [ -n "$CLOUD_SQL_INSTANCES" ]; then
    echo "✅ Conexão Cloud SQL configurada: $CLOUD_SQL_INSTANCES"
else
    echo "❌ Conexão Cloud SQL NÃO configurada"
fi

echo ""
echo "=========================================="
echo "✅ VERIFICAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
echo "📝 Resumo:"
echo "  - Revisão: $LATEST_REVISION"
echo "  - Status HTTP: $HTTP_CODE"
echo "  - Conexão Cloud SQL: $([ -n "$CLOUD_SQL_INSTANCES" ] && echo "✅ Configurada" || echo "❌ Não configurada")"
echo ""
echo "🔗 URL: $SERVICE_URL"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "🎉 SUCESSO! O serviço está funcionando corretamente!"
    echo ""
    echo "Você pode acessar o sistema em:"
    echo "  $SERVICE_URL"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "⚠️ Ainda há erro 500. Verifique os logs acima para mais detalhes."
elif [ "$HTTP_CODE" = "400" ]; then
    echo "⚠️ Erro 400. O middleware pode precisar de ajustes."
    echo "   Verifique se o código do middleware foi atualizado no deploy."
fi
echo ""





