#!/bin/bash
# Script para verificar o status completo do deploy

SERVICE_NAME="monpec"
REGION="us-central1"

echo "========================================"
echo "🔍 Verificação Completa do Deploy"
echo "========================================"
echo ""

# 1. Verificar serviço
echo "1️⃣  Verificando serviço Cloud Run..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    echo "✅ Serviço ativo: $SERVICE_URL"
else
    echo "❌ Serviço não encontrado"
    exit 1
fi
echo ""

# 2. Verificar variáveis de ambiente
echo "2️⃣  Verificando variáveis de ambiente..."
ENV_VARS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null)
if [ -n "$ENV_VARS" ]; then
    echo "✅ Variáveis configuradas:"
    echo "$ENV_VARS" | tr ',' '\n' | head -10
    echo ""
    
    # Verificar se variáveis críticas estão presentes
    if echo "$ENV_VARS" | grep -q "MERCADOPAGO_ACCESS_TOKEN"; then
        echo "  ✅ MERCADOPAGO_ACCESS_TOKEN: Configurado"
    else
        echo "  ⚠️  MERCADOPAGO_ACCESS_TOKEN: NÃO configurado"
    fi
    
    if echo "$ENV_VARS" | grep -q "SECRET_KEY"; then
        echo "  ✅ SECRET_KEY: Configurado"
    else
        echo "  ⚠️  SECRET_KEY: NÃO configurado"
    fi
    
    if echo "$ENV_VARS" | grep -q "DB_HOST"; then
        echo "  ✅ DB_HOST: Configurado"
    else
        echo "  ⚠️  DB_HOST: NÃO configurado"
    fi
else
    echo "⚠️  Nenhuma variável de ambiente encontrada"
fi
echo ""

# 3. Verificar domínios
echo "3️⃣  Verificando mapeamentos de domínio..."
echo "Domínio monpec.com.br:"
gcloud alpha run domain-mappings describe monpec.com.br --region $REGION 2>/dev/null | grep -E "name|status|dns" || echo "  ⚠️  Não encontrado ou erro"
echo ""
echo "Domínio www.monpec.com.br:"
gcloud alpha run domain-mappings describe www.monpec.com.br --region $REGION 2>/dev/null | grep -E "name|status|dns" || echo "  ⚠️  Não encontrado ou erro"
echo ""

# 4. Verificar job de migração
echo "4️⃣  Verificando job de migração..."
JOB_EXISTS=$(gcloud run jobs describe migrate-monpec --region $REGION 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Job migrate-monpec existe"
    echo ""
    echo "Últimas execuções:"
    gcloud run jobs executions list --job migrate-monpec --region $REGION --limit 3 2>/dev/null | head -5
else
    echo "⚠️  Job migrate-monpec não encontrado"
fi
echo ""

# 5. Verificar logs recentes
echo "5️⃣  Verificando logs recentes (últimas 10 linhas)..."
gcloud run services logs read $SERVICE_NAME --region $REGION --limit 10 2>/dev/null | tail -10
echo ""

# 6. Testar URL
echo "6️⃣  Testando acesso ao serviço..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço respondendo (HTTP $HTTP_CODE)"
else
    echo "⚠️  Serviço não está respondendo corretamente (HTTP $HTTP_CODE)"
fi
echo ""

echo "========================================"
echo "✅ Verificação concluída"
echo "========================================"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure o DNS do www.monpec.com.br (veja CONFIGURAR_DNS.txt)"
echo "2. Configure as variáveis de ambiente (execute CONFIGURAR_VARIAVEIS_FINAL.sh)"
echo "3. Aguarde a propagação DNS e teste: https://www.monpec.com.br"
echo ""




























