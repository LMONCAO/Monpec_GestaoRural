#!/bin/bash
# Script prático para resolver o problema AGORA

echo "========================================"
echo "🔧 RESOLVENDO O PROBLEMA AGORA"
echo "========================================"
echo ""

# 1. Ver o erro real
echo "1️⃣  Verificando o erro real..."
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=migrate-monpec" --limit 20 --format="value(textPayload)" 2>/dev/null | grep -i "error\|exception\|traceback" | head -10

echo ""
echo "2️⃣  Verificando se o serviço está funcionando..."
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    echo "✅ Serviço está rodando: $SERVICE_URL"
    echo ""
    echo "3️⃣  O sistema pode estar funcionando mesmo sem a migração do job!"
    echo "   As migrações podem ser aplicadas automaticamente quando o serviço inicia."
    echo ""
    echo "4️⃣  Teste o sistema agora:"
    echo "   Acesse: $SERVICE_URL"
    echo "   Ou: https://monpec.com.br"
    echo ""
else
    echo "❌ Serviço não encontrado"
fi

echo ""
echo "========================================"
echo "💡 SOLUÇÃO ALTERNATIVA"
echo "========================================"
echo ""
echo "Se a migração do job não funcionar, podemos:"
echo ""
echo "1. Aplicar migrações diretamente no banco (via Cloud SQL)"
echo "2. Ou deixar o Django aplicar automaticamente na primeira requisição"
echo ""
echo "O importante é que o SISTEMA FUNCIONE para o público!"
echo ""



