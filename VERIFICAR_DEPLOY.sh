#!/bin/bash
# Script para verificar se o deploy funcionou
# Execute no Cloud Shell

echo "========================================"
echo "  VERIFICANDO STATUS DO DEPLOY"
echo "========================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

# 1. Verificar se o serviço existe
echo "1. Verificando se o serviço existe..."
if gcloud run services describe $SERVICE_NAME --region $REGION > /dev/null 2>&1; then
    echo "✅ Serviço '$SERVICE_NAME' encontrado!"
else
    echo "❌ Serviço '$SERVICE_NAME' NÃO encontrado!"
    echo "   O deploy pode não ter sido concluído."
    exit 1
fi
echo ""

# 2. Obter URL do serviço
echo "2. Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    echo "✅ URL do serviço:"
    echo "   $SERVICE_URL"
else
    echo "❌ Não foi possível obter a URL"
fi
echo ""

# 3. Verificar status do serviço
echo "3. Verificando status do serviço..."
STATUS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)" 2>/dev/null)
if [ "$STATUS" = "True" ]; then
    echo "✅ Serviço está RODANDO e FUNCIONANDO!"
else
    echo "⚠️  Status: $STATUS"
    echo "   Verifique os logs para mais detalhes"
fi
echo ""

# 4. Verificar última revisão
echo "4. Verificando última revisão..."
LATEST_REVISION=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.latestReadyRevisionName)" 2>/dev/null)
if [ -n "$LATEST_REVISION" ]; then
    echo "✅ Última revisão: $LATEST_REVISION"
else
    echo "❌ Não foi possível obter a revisão"
fi
echo ""

# 5. Testar acesso HTTP
echo "5. Testando acesso HTTP..."
if [ -n "$SERVICE_URL" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$SERVICE_URL" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        echo "✅ Serviço está RESPONDENDO! (HTTP $HTTP_CODE)"
        echo "   O sistema está FUNCIONANDO na web!"
    elif [ "$HTTP_CODE" = "000" ]; then
        echo "⚠️  Não foi possível conectar (timeout ou erro de rede)"
    elif [ "$HTTP_CODE" = "500" ]; then
        echo "❌ Erro 500 - Internal Server Error"
        echo "   O serviço está rodando mas há um erro na aplicação"
        echo "   Verifique os logs abaixo"
    else
        echo "⚠️  Código HTTP: $HTTP_CODE"
        echo "   Verifique os logs para mais detalhes"
    fi
else
    echo "⚠️  URL não disponível para teste"
fi
echo ""

# 6. Ver últimos logs
echo "6. Últimos logs do serviço (últimas 20 linhas):"
echo "----------------------------------------"
gcloud run services logs read $SERVICE_NAME --region $REGION --limit=20 2>/dev/null | head -20 || echo "Não foi possível obter logs"
echo "----------------------------------------"
echo ""

# 7. Resumo final
echo "========================================"
echo "  RESUMO"
echo "========================================"
if [ -n "$SERVICE_URL" ] && [ "$STATUS" = "True" ]; then
    echo "✅ DEPLOY FUNCIONANDO!"
    echo ""
    echo "🌐 Acesse o sistema em:"
    echo "   $SERVICE_URL"
    echo ""
    echo "📋 Próximos passos:"
    echo "   1. Abra a URL no navegador"
    echo "   2. Teste fazer login"
    echo "   3. Se houver erros, veja os logs acima"
else
    echo "⚠️  Verifique os problemas acima"
    echo ""
    echo "🔍 Para mais detalhes, execute:"
    echo "   gcloud run services describe $SERVICE_NAME --region $REGION"
    echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50"
fi
echo "========================================"
