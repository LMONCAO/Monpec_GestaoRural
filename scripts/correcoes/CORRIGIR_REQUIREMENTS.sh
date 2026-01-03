#!/bin/bash
# Remover django-logging e garantir build funcione

echo "Removendo django-logging do requirements_producao.txt..."

# Remover linha com django-logging
sed -i '/django-logging/d' requirements_producao.txt

# Verificar se foi removido
if grep -q "django-logging" requirements_producao.txt; then
    echo "⚠️  Ainda há django-logging no arquivo"
else
    echo "✅ django-logging removido"
fi

echo ""
echo "Fazendo build..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec:latest




























