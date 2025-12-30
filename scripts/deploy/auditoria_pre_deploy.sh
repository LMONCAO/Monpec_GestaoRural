#!/bin/bash
# Script de Auditoria Pré-Deploy
# Verifica todos os componentes antes do deploy

set -e

echo "========================================"
echo "🔍 AUDITORIA PRÉ-DEPLOY - SISTEMA MONPEC"
echo "========================================"
echo ""

ERROS=0
AVISOS=0

# Função para verificar erro
verificar_erro() {
    if [ $? -ne 0 ]; then
        echo "❌ ERRO: $1"
        ERROS=$((ERROS + 1))
        return 1
    else
        echo "✅ OK: $1"
        return 0
    fi
}

# Função para aviso
aviso() {
    echo "⚠️ AVISO: $1"
    AVISOS=$((AVISOS + 1))
}

# 1. Verificar Dockerfile
echo "📋 1. Verificando Dockerfile.prod..."
if [ ! -f "Dockerfile.prod" ]; then
    echo "❌ ERRO: Dockerfile.prod não encontrado!"
    ERROS=$((ERROS + 1))
else
    if [ ! -s "Dockerfile.prod" ]; then
        echo "❌ ERRO: Dockerfile.prod está vazio!"
        ERROS=$((ERROS + 1))
    else
        echo "✅ Dockerfile.prod existe e não está vazio"
        # Verificar se tem comandos essenciais
        if ! grep -q "FROM python" Dockerfile.prod; then
            echo "❌ ERRO: Dockerfile.prod não tem FROM python"
            ERROS=$((ERROS + 1))
        fi
        if ! grep -q "CMD" Dockerfile.prod; then
            echo "❌ ERRO: Dockerfile.prod não tem CMD"
            ERROS=$((ERROS + 1))
        fi
    fi
fi
echo ""

# 2. Verificar requirements
echo "📦 2. Verificando requirements..."
if [ ! -f "requirements_producao.txt" ]; then
    echo "❌ ERRO: requirements_producao.txt não encontrado!"
    ERROS=$((ERROS + 1))
else
    echo "✅ requirements_producao.txt existe"
    # Verificar dependências críticas
    DEPENDENCIAS_CRITICAS=("Django" "gunicorn" "psycopg2-binary" "whitenoise" "openpyxl")
    for dep in "${DEPENDENCIAS_CRITICAS[@]}"; do
        if ! grep -qi "$dep" requirements_producao.txt; then
            echo "❌ ERRO: $dep não encontrado em requirements_producao.txt"
            ERROS=$((ERROS + 1))
        else
            echo "  ✅ $dep encontrado"
        fi
    done
fi
echo ""

# 3. Verificar settings
echo "⚙️ 3. Verificando settings..."
if [ ! -f "sistema_rural/settings_gcp.py" ]; then
    echo "❌ ERRO: sistema_rural/settings_gcp.py não encontrado!"
    ERROS=$((ERROS + 1))
else
    echo "✅ settings_gcp.py existe"
    # Verificar SECRET_KEY (não crítico - será configurada via env var no deploy)
    if ! grep -q "SECRET_KEY" sistema_rural/settings_gcp.py; then
        echo "⚠️ AVISO: SECRET_KEY não encontrada em settings_gcp.py (será configurada via variável de ambiente no deploy)"
        AVISOS=$((AVISOS + 1))
    else
        echo "  ✅ SECRET_KEY encontrada (será sobrescrita por variável de ambiente no deploy)"
    fi
    # Verificar DATABASES
    if ! grep -q "DATABASES" sistema_rural/settings_gcp.py; then
        echo "❌ ERRO: Configuração de DATABASES não encontrada"
        ERROS=$((ERROS + 1))
    else
        echo "  ✅ Configuração de DATABASES encontrada"
    fi
fi
echo ""

# 4. Verificar manage.py
echo "🐍 4. Verificando manage.py..."
if [ ! -f "manage.py" ]; then
    echo "❌ ERRO: manage.py não encontrado!"
    ERROS=$((ERROS + 1))
else
    echo "✅ manage.py existe"
fi
echo ""

# 5. Verificar comando garantir_admin
echo "👤 5. Verificando comando garantir_admin..."
if [ ! -f "gestao_rural/management/commands/garantir_admin.py" ]; then
    echo "❌ ERRO: garantir_admin.py não encontrado!"
    ERROS=$((ERROS + 1))
else
    echo "✅ garantir_admin.py existe"
fi
echo ""

# 6. Verificar estrutura de diretórios
echo "📁 6. Verificando estrutura de diretórios..."
DIRETORIOS_CRITICOS=("gestao_rural" "sistema_rural" "templates" "static")
for dir in "${DIRETORIOS_CRITICOS[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ ERRO: Diretório $dir não encontrado!"
        ERROS=$((ERROS + 1))
    else
        echo "  ✅ $dir existe"
    fi
done
echo ""

# 7. Verificar arquivos estáticos
echo "🎨 7. Verificando arquivos estáticos..."
if [ ! -d "static" ]; then
    aviso "Diretório static não encontrado (pode ser normal se usar collectstatic)"
else
    echo "✅ Diretório static existe"
    if [ -z "$(ls -A static 2>/dev/null)" ]; then
        aviso "Diretório static está vazio"
    fi
fi
echo ""

# 8. Verificar .gitignore (para não enviar arquivos desnecessários)
echo "📝 8. Verificando .gitignore..."
if [ ! -f ".gitignore" ]; then
    aviso ".gitignore não encontrado"
else
    echo "✅ .gitignore existe"
fi
echo ""

# Resumo
echo "========================================"
echo "📊 RESUMO DA AUDITORIA"
echo "========================================"
echo "❌ Erros encontrados: $ERROS"
echo "⚠️ Avisos: $AVISOS"
echo ""

if [ $ERROS -eq 0 ]; then
    echo "✅✅✅ AUDITORIA PASSOU! Sistema pronto para deploy."
    echo ""
    exit 0
else
    echo "❌❌❌ AUDITORIA FALHOU! Corrija os erros antes de fazer deploy."
    echo ""
    exit 1
fi

