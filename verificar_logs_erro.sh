#!/bin/bash
# 🔍 Script para verificar logs do Cloud Run e identificar o erro

echo "🔍 VERIFICANDO LOGS DO CLOUD RUN"
echo "========================================"
echo ""

# Verificar logs recentes
echo "📋 Últimos 50 logs do serviço 'monpec':"
echo ""
gcloud run services logs read monpec --region us-central1 --limit 50

echo ""
echo "========================================"
echo "📋 Para ver logs em tempo real, execute:"
echo "   gcloud run services logs tail monpec --region us-central1"
echo ""

