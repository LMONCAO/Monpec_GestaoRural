#!/bin/bash
# Script para configurar domínio monpec.com.br no Cloud Run

set -e

echo "🌐 Configurando Domínio monpec.com.br"
echo "========================================"
echo ""

# 1. Verificar domínio
echo "📋 Verificando domínio..."
gcloud domains list-user-verified 2>/dev/null | grep -q "monpec.com.br" && echo "✅ Domínio verificado" || echo "⚠️  Domínio não verificado (será verificado automaticamente)"
echo ""

# 2. Mapear domínio principal
echo "🔗 Mapeando monpec.com.br..."
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1 \
    --quiet 2>/dev/null || echo "⚠️  Mapeamento pode já existir"

echo ""

# 3. Mapear www (opcional)
echo "🔗 Mapeando www.monpec.com.br..."
gcloud run domain-mappings create \
    --service monpec \
    --domain www.monpec.com.br \
    --region us-central1 \
    --quiet 2>/dev/null || echo "⚠️  Mapeamento pode já existir"

echo ""

# 4. Obter informações de DNS
echo "========================================"
echo "📋 INFORMAÇÕES DE DNS"
echo "========================================"
echo ""

echo "Para monpec.com.br:"
gcloud run domain-mappings describe monpec.com.br --region us-central1 --format="value(metadata.annotations.'run.googleapis.com/ingress-status')" 2>/dev/null || echo "Verifique manualmente no console"

echo ""
echo "Para www.monpec.com.br:"
gcloud run domain-mappings describe www.monpec.com.br --region us-central1 --format="value(metadata.annotations.'run.googleapis.com/ingress-status')" 2>/dev/null || echo "Verifique manualmente no console"

echo ""
echo "========================================"
echo "📝 PRÓXIMOS PASSOS"
echo "========================================"
echo ""
echo "1. Execute o comando abaixo para ver as instruções de DNS:"
echo "   gcloud run domain-mappings describe monpec.com.br --region us-central1"
echo ""
echo "2. Configure os registros DNS no seu provedor (Registro.br, etc.)"
echo ""
echo "3. Aguarde a propagação DNS (15 minutos a 48 horas)"
echo ""
echo "4. Verifique o status:"
echo "   gcloud run domain-mappings describe monpec.com.br --region us-central1"
echo ""














