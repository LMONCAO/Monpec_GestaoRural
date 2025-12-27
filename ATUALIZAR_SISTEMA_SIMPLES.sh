#!/bin/bash
# Script SIMPLES para atualizar o sistema

echo "Atualizando sistema no Google Cloud..."
echo ""

# 1. Fazer build da nova versão
echo "1. Fazendo build..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest

# 2. Fazer deploy (isso atualiza o sistema)
echo ""
echo "2. Fazendo deploy (atualizando sistema)..."
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi --cpu 1 --port 8080

echo ""
echo "Pronto! Aguarde 1-2 minutos e teste: https://monpec.com.br"
echo ""





















