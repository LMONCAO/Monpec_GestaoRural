#!/bin/bash
# 🔍 VERIFICAÇÃO RÁPIDA DO STATUS - CLOUD RUN

echo "🔍 VERIFICAÇÃO RÁPIDA - MONPEC.COM.BR"
echo "======================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DOMAIN="monpec.com.br"

# Configurar projeto
gcloud config set project $PROJECT_ID >/dev/null 2>&1

# Verificar serviço
echo "📊 Status do serviço Cloud Run:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'table(
    metadata.name,
    status.url,
    status.conditions[0].status,
    status.conditions[0].message
)' 2>/dev/null || echo "❌ Serviço não encontrado"

echo ""

# Verificar domínio
echo "🌐 Status do domínio:"
gcloud run domain-mappings describe $DOMAIN --region $REGION --format 'table(
    metadata.name,
    status.conditions[0].status,
    status.conditions[0].message
)' 2>/dev/null || echo "⚠️  Domínio não mapeado"

echo ""

# Testar URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    echo "🧪 Testando conectividade:"
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$SERVICE_URL" 2>/dev/null)
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
        echo "   ✅ Serviço respondendo (HTTP $HTTP_STATUS)"
    else
        echo "   ❌ Serviço não responde (HTTP $HTTP_STATUS)"
    fi
    echo "   URL: $SERVICE_URL"
fi

echo ""
echo "💡 Para diagnóstico completo: bash CORRIGIR_503_CLOUD_RUN.sh"


























