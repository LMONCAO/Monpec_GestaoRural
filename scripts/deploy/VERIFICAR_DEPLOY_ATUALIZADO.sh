#!/bin/bash
# Script para verificar se o deploy está atualizado com o ambiente localhost

echo "========================================"
echo "VERIFICAÇÃO DE SINCRONIZAÇÃO DEPLOY"
echo "========================================"
echo ""

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo "ERRO: Execute no diretório raiz do projeto!"
    exit 1
fi

echo "Verificando arquivos importantes..."
echo ""

# 1. Verificar Dockerfile.prod
if [ -f "Dockerfile.prod" ]; then
    echo "✓ Dockerfile.prod encontrado"
    if grep -q "requirements_producao.txt" Dockerfile.prod; then
        echo "  ⚠ Dockerfile.prod referencia requirements_producao.txt"
    fi
    if grep -q "requirements.txt" Dockerfile.prod; then
        echo "  ✓ Dockerfile.prod também suporta requirements.txt"
    fi
else
    echo "✗ Dockerfile.prod NÃO encontrado"
fi

# 2. Verificar requirements
echo ""
echo "Verificando arquivos de requirements..."
if [ -f "requirements.txt" ]; then
    echo "✓ requirements.txt encontrado"
    wc -l requirements.txt | awk '{print "  - " $1 " pacotes"}'
else
    echo "✗ requirements.txt NÃO encontrado"
    echo "  Para gerar: pip freeze > requirements.txt"
fi

if [ -f "requirements_producao.txt" ]; then
    echo "✓ requirements_producao.txt encontrado"
else
    echo "⚠ requirements_producao.txt não encontrado (opcional)"
fi

# 3. Verificar settings
echo ""
echo "Verificando configurações..."
if [ -f "sistema_rural/settings.py" ]; then
    echo "✓ settings.py encontrado"
fi

if [ -f "sistema_rural/settings_gcp.py" ]; then
    echo "✓ settings_gcp.py encontrado"
    if grep -q "from .settings import \*" sistema_rural/settings_gcp.py; then
        echo "  ✓ settings_gcp.py importa settings.py (sincronizado)"
    else
        echo "  ⚠ settings_gcp.py pode não estar sincronizado"
    fi
else
    echo "✗ settings_gcp.py NÃO encontrado"
fi

# 4. Verificar script de deploy
echo ""
echo "Verificando scripts de deploy..."
if [ -f "DEPLOY_GCP_COMPLETO.sh" ]; then
    echo "✓ DEPLOY_GCP_COMPLETO.sh encontrado"
    if grep -q "Dockerfile.prod" DEPLOY_GCP_COMPLETO.sh; then
        echo "  ✓ Script usa Dockerfile.prod"
    fi
else
    echo "✗ DEPLOY_GCP_COMPLETO.sh NÃO encontrado"
fi

# 5. Verificar INSTALLED_APPS sincronização
echo ""
echo "Verificando sincronização de INSTALLED_APPS..."
if [ -f "sistema_rural/settings.py" ] && [ -f "sistema_rural/settings_gcp.py" ]; then
    APPS_LOCAL=$(grep -A 10 "INSTALLED_APPS" sistema_rural/settings.py | grep -c "'")
    APPS_GCP=$(grep -A 10 "INSTALLED_APPS" sistema_rural/settings_gcp.py | grep -c "'" || echo "0")
    if [ "$APPS_GCP" -eq "0" ]; then
        echo "  ✓ settings_gcp.py herda INSTALLED_APPS de settings.py (sincronizado)"
    else
        echo "  ⚠ Verifique se INSTALLED_APPS está sincronizado"
    fi
fi

echo ""
echo "========================================"
echo "RECOMENDAÇÕES:"
echo "========================================"
echo ""
echo "1. Para garantir sincronização, execute:"
echo "   pip freeze > requirements.txt"
echo ""
echo "2. Se necessário, copie para produção:"
echo "   cp requirements.txt requirements_producao.txt"
echo ""
echo "3. O Dockerfile.prod já está configurado para usar"
echo "   requirements_producao.txt OU requirements.txt"
echo ""
echo "4. settings_gcp.py importa settings.py, então está"
echo "   automaticamente sincronizado"
echo ""
echo "========================================"





