#!/bin/bash
# Script para verificar e corrigir problema de login

echo "🔍 DIAGNÓSTICO DE LOGIN"
echo "======================="
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

# 1. Verificar serviços
echo "▶ 1. Verificando serviços Cloud Run:"
gcloud run services list --region $REGION --format="table(metadata.name,status.url,status.latestReadyRevisionName)"

echo ""
echo "▶ 2. URL do serviço 'monpec':"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)' 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    echo "   $SERVICE_URL"
else
    echo "   ❌ Serviço não encontrado!"
    exit 1
fi

echo ""
echo "▶ 3. Verificando mapeamento de domínio:"
DOMAIN_MAPPING=$(gcloud run domain-mappings describe monpec.com.br --region $REGION --format='value(spec.routeName)' 2>/dev/null)
if [ -n "$DOMAIN_MAPPING" ]; then
    echo "   Domínio monpec.com.br está mapeado para: $DOMAIN_MAPPING"
else
    echo "   ⚠️  Domínio não está mapeado ou não existe"
fi

echo ""
echo "▶ 4. Testando URL direta do Cloud Run:"
echo "   Acesse: $SERVICE_URL/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""

echo "▶ 5. Para recriar admin no banco:"
echo "   Execute o job novamente:"
echo "   gcloud run jobs execute create-admin --region $REGION --wait"
echo ""

echo "💡 IMPORTANTE:"
echo "   - Tente fazer login usando a URL direta primeiro: $SERVICE_URL/login/"
echo "   - Use 'admin' como usuário (não admin@monpec.com.br)"
echo "   - Se funcionar na URL direta mas não em monpec.com.br, o domínio está usando serviço/banco diferente"








