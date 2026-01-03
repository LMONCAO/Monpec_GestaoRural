#!/bin/bash
# Script para verificar qual serviço Cloud Run está ativo

echo "🔍 Verificando serviços Cloud Run..."
echo ""

# Listar todos os serviços
echo "▶ Serviços Cloud Run disponíveis:"
gcloud run services list --region us-central1 --format="table(metadata.name,status.url,status.conditions[0].status)"

echo ""
echo "▶ Verificando serviço 'monpec':"
gcloud run services describe monpec --region us-central1 --format="value(status.url)"

echo ""
echo "▶ Verificando domínio personalizado:"
gcloud run domain-mappings list --region us-central1

echo ""
echo "▶ Testando conexão com o banco de dados:"
echo "   (Execute criar_admin_producao.py novamente se necessário)"








