#!/bin/bash
# Script para corrigir comandos com erro de região

SERVICE_NAME="monpec"
REGION_CORRETO="us-central1"  # CORRIGIDO
REGION_ERRADO="us-centrall"   # ERRADO

echo "========================================"
echo "🔧 Corrigindo Comandos com Região Errada"
echo "========================================"
echo ""
echo "⚠️  ATENÇÃO: O erro 'us-centrall' foi corrigido para 'us-central1'"
echo ""

# Comandos corretos
echo "Comandos corretos para executar:"
echo ""
echo "# 1. Deploy"
echo "gcloud run deploy $SERVICE_NAME \\"
echo "    --image gcr.io/monpec-sistema-rural/monpec:latest \\"
echo "    --region $REGION_CORRETO \\"
echo "    --platform managed \\"
echo "    --allow-unauthenticated \\"
echo "    --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br' \\"
echo "    --update-env-vars 'MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/' \\"
echo "    --memory 1Gi --cpu 1 --timeout 300 --max-instances 10 --min-instances 1 --port 8080"
echo ""
echo "# 2. Domínio"
echo "gcloud run domain-mappings create --service $SERVICE_NAME --domain monpec.com.br --region $REGION_CORRETO"
echo "gcloud run domain-mappings create --service $SERVICE_NAME --domain www.monpec.com.br --region $REGION_CORRETO"
echo ""
echo "# 3. Migrações"
echo "gcloud run jobs create migrate-monpec \\"
echo "    --image gcr.io/monpec-sistema-rural/monpec:latest \\"
echo "    --region $REGION_CORRETO \\"
echo "    --command python \\"
echo "    --args 'manage.py,migrate' \\"
echo "    --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'"
echo ""
echo "gcloud run jobs execute migrate-monpec --region $REGION_CORRETO"
echo ""



