#!/bin/bash
# Script para corrigir o requirements_producao.txt no Cloud Shell
# Execute este comando no Cloud Shell

echo "🔧 Corrigindo requirements_producao.txt..."
echo ""

# Entrar na pasta do projeto (ajuste o nome se necessário)
cd Monpec_GestaoRural 2>/dev/null || cd . 2>/dev/null

# Verificar se o arquivo existe
if [ ! -f "requirements_producao.txt" ]; then
    echo "❌ Arquivo requirements_producao.txt não encontrado!"
    echo "   Certifique-se de estar na pasta correta do projeto"
    echo "   Execute: ls -la para ver os arquivos"
    exit 1
fi

# Fazer backup
cp requirements_producao.txt requirements_producao.txt.backup
echo "✅ Backup criado: requirements_producao.txt.backup"

# Remover a linha problemática
sed -i 's/^django-logging==0.1.0/# django-logging==0.1.0  # Removido: pacote não existe no PyPI/' requirements_producao.txt

# Verificar se foi removido
if grep -q "^django-logging==0.1.0" requirements_producao.txt; then
    echo "⚠️  Ainda encontrou django-logging. Removendo manualmente..."
    sed -i '/^django-logging==0.1.0$/d' requirements_producao.txt
fi

# Corrigir Dockerfile também
if [ -f "Dockerfile" ]; then
    echo "🔧 Corrigindo Dockerfile..."
    cp Dockerfile Dockerfile.backup
    # Remover linha redundante do gunicorn (já está no requirements)
    sed -i '/pip install --no-cache-dir gunicorn$/d' Dockerfile
    echo "✅ Dockerfile corrigido"
fi

echo ""
echo "✅ Correção aplicada!"
echo ""
echo "📋 Verificação:"
grep -n "django-logging" requirements_producao.txt || echo "   ✅ django-logging removido com sucesso"
echo ""
echo "🚀 Agora execute o deploy novamente:"
echo "   gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec"
echo ""

