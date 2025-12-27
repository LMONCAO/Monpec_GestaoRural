#!/bin/bash
# Script para executar limpeza de usuários no Cloud Run
# Execute este script após o deploy

echo "🔧 Executando limpeza de usuários..."

# Executar comando de limpeza via Cloud Run
gcloud run jobs execute limpar-usuarios-job \
    --region us-central1 \
    --wait || \
    echo "⚠️ Job não existe. Execute manualmente: python manage.py limpar_usuarios --confirmar"

echo "✅ Limpeza concluída!"


