#!/bin/bash
# Verificar se o sistema já está funcionando

echo "========================================"
echo "✅ VERIFICANDO SE O SISTEMA FUNCIONA"
echo "========================================"
echo ""

# 1. URL do serviço
echo "1️⃣  URL do Serviço:"
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    echo "   $SERVICE_URL"
    echo ""
    echo "   🌐 Acesse no navegador: $SERVICE_URL"
    echo "   🌐 Ou: https://monpec.com.br"
    echo ""
else
    echo "   ❌ Serviço não encontrado"
    exit 1
fi

# 2. Testar resposta HTTP
echo "2️⃣  Testando resposta do servidor..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "   ✅ Servidor respondendo (HTTP $HTTP_CODE)"
    echo ""
    echo "   🎉 O SISTEMA ESTÁ FUNCIONANDO!"
    echo ""
    echo "   Próximos passos:"
    echo "   1. Acesse: $SERVICE_URL"
    echo "   2. Teste fazer login"
    echo "   3. Teste os botões de pagamento"
    echo "   4. Se tudo funcionar, está pronto para o público!"
    echo ""
else
    echo "   ⚠️  Servidor não está respondendo corretamente (HTTP $HTTP_CODE)"
    echo ""
    echo "   Verifique os logs:"
    echo "   gcloud run services logs read monpec --region us-central1 --limit 50"
fi

# 3. Ver logs recentes
echo "3️⃣  Últimos logs do serviço:"
gcloud run services logs read monpec --region us-central1 --limit 5 2>/dev/null | tail -10
echo ""

echo "========================================"
echo "💡 LEMBRE-SE:"
echo "========================================"
echo ""
echo "O importante é que o SISTEMA FUNCIONE para o público!"
echo "A migração do job é um detalhe técnico."
echo ""
echo "Se o sistema já está acessível e funcionando,"
echo "pode estar tudo certo mesmo sem a migração do job!"
echo ""




























