#!/bin/bash
# Script para configurar domínio personalizado no Cloud Run

SERVICE_NAME="monpec"
REGION="us-central1"

echo "========================================"
echo "Configurando domínio personalizado"
echo "========================================"
echo ""

echo "Criando mapeamento para monpec.com.br..."
gcloud run domain-mappings create \
    --service $SERVICE_NAME \
    --domain monpec.com.br \
    --region $REGION

echo ""
echo "Criando mapeamento para www.monpec.com.br..."
gcloud run domain-mappings create \
    --service $SERVICE_NAME \
    --domain www.monpec.com.br \
    --region $REGION

echo ""
echo "========================================"
echo "Domínio configurado!"
echo "========================================"
echo ""
echo "IMPORTANTE: Configure os registros DNS no seu provedor de domínio"
echo "Os registros serão exibidos após a criação do mapeamento."
echo ""



