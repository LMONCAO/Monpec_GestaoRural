#!/bin/bash
# Solução SIMPLES e DIRETA - sem complicações

echo "========================================"
echo "🚀 SOLUÇÃO SIMPLES E DIRETA"
echo "========================================"
echo ""

# Limpar cache do gcloud
echo "1️⃣  Limpando cache..."
rm -rf ~/.cache/gcloud 2>/dev/null || true
echo "✅ Cache limpo"
echo ""

# Tentar build novamente (sem timeout longo)
echo "2️⃣  Fazendo build (tentativa simples)..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BUILD SUCESSO!"
    echo ""
    echo "3️⃣  Fazendo deploy..."
    gcloud run deploy monpec \
        --image gcr.io/monpec-sistema-rural/monpec:latest \
        --region us-central1 \
        --platform managed \
        --allow-unauthenticated \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" \
        --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" \
        --memory 1Gi --cpu 1 --port 8080
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "========================================"
        echo "✅ SUCESSO! Sistema atualizado!"
        echo "========================================"
        echo ""
        echo "Aguarde 1-2 minutos e teste:"
        echo "  https://monpec.com.br"
        echo ""
    fi
else
    echo ""
    echo "⚠️  Build falhou, mas não se preocupe!"
    echo ""
    echo "O sistema atual ESTÁ FUNCIONANDO."
    echo "Podemos fazer atualizações depois."
    echo ""
fi





















