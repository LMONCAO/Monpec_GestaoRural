#!/bin/bash
# Script para configurar domínio personalizado no Cloud Run
# Uso: ./configurar-dominio.sh [PROJECT_ID] [REGION] [DOMAIN]

set -e

PROJECT_ID=${1:-"SEU_PROJECT_ID"}
REGION=${2:-"us-central1"}
DOMAIN=${3:-"monpec.com.br"}
SERVICE_NAME="monpec"

echo "🌐 Configurando domínio personalizado: ${DOMAIN}"

# Mapear domínio
gcloud run domain-mappings create \
    --service ${SERVICE_NAME} \
    --domain ${DOMAIN} \
    --region ${REGION}

echo "✅ Domínio configurado!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure os registros DNS conforme mostrado acima"
echo "2. Aguarde a propagação DNS (pode levar até 24 horas)"
echo "3. Verifique o status: gcloud run domain-mappings describe ${DOMAIN} --region ${REGION}"




















