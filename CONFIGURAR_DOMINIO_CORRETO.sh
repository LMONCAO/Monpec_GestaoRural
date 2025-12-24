#!/bin/bash
# Script CORRIGIDO para configurar domínio
# Usa gcloud alpha/beta para domain-mappings

SERVICE_NAME="monpec"
REGION="us-central1"

echo "========================================"
echo "🌐 Configurando Domínio Personalizado"
echo "========================================"
echo ""

# Tentar com alpha primeiro
echo "Criando mapeamento para monpec.com.br..."
gcloud alpha run domain-mappings create \
    --service $SERVICE_NAME \
    --domain monpec.com.br \
    --region $REGION 2>/dev/null || \
gcloud beta run domain-mappings create \
    --service $SERVICE_NAME \
    --domain monpec.com.br \
    --region $REGION 2>/dev/null || \
echo "⚠️  Domínio monpec.com.br já existe ou erro ao criar"

echo ""
echo "Criando mapeamento para www.monpec.com.br..."
gcloud alpha run domain-mappings create \
    --service $SERVICE_NAME \
    --domain www.monpec.com.br \
    --region $REGION 2>/dev/null || \
gcloud beta run domain-mappings create \
    --service $SERVICE_NAME \
    --domain www.monpec.com.br \
    --region $REGION 2>/dev/null || \
echo "⚠️  Domínio www.monpec.com.br já existe ou erro ao criar"

echo ""
echo "========================================"
echo "✅ Domínios configurados!"
echo "========================================"
echo ""
echo "📋 Próximos passos:"
echo "1. Verifique os registros DNS fornecidos:"
echo "   gcloud alpha run domain-mappings describe monpec.com.br --region $REGION"
echo ""
echo "2. Configure os registros DNS no seu provedor de domínio"
echo ""



