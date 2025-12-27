#!/bin/bash
# Corrigir build e fazer deploy correto

echo "========================================"
echo "🔧 Corrigindo Build e Fazendo Deploy"
echo "========================================"
echo ""

# Verificar se há django-logging no requirements
echo "1️⃣  Verificando requirements..."
if grep -q "django-logging" requirements_producao.txt 2>/dev/null; then
    echo "⚠️  Removendo django-logging do requirements..."
    sed -i '/django-logging/d' requirements_producao.txt
    echo "✅ Removido"
else
    echo "✅ django-logging não está no requirements_producao.txt"
fi
echo ""

# Build com região correta
echo "2️⃣  Fazendo build (isso pode levar alguns minutos)..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Build falhou!"
    echo ""
    echo "Verifique os erros acima e corrija o requirements_producao.txt"
    exit 1
fi

echo ""
echo "✅ Build concluído!"
echo ""

# Deploy com região CORRETA (us-central1, não us-centrall)
echo "3️⃣  Fazendo deploy com região CORRETA..."
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" \
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ DEPLOY CONCLUÍDO!"
    echo "========================================"
    echo ""
    echo "Aguarde 1-2 minutos e teste:"
    echo "  https://monpec.com.br"
    echo ""
    echo "Limpe o cache do navegador (Ctrl+Shift+Delete) ou use aba anônima"
    echo ""
else
    echo ""
    echo "❌ Deploy falhou"
    exit 1
fi





















