#!/bin/bash
# Script de verificação pré-deploy

echo "🔍 VERIFICAÇÃO PRÉ-DEPLOY - MONPEC"
echo "=================================="
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está na pasta correta
echo "📁 Verificando estrutura de arquivos..."
if [ -f "manage.py" ]; then
    echo -e "${GREEN}✅ manage.py encontrado${NC}"
else
    echo -e "${RED}❌ manage.py NÃO encontrado - você está na pasta errada!${NC}"
    exit 1
fi

if [ -f "Dockerfile" ]; then
    echo -e "${GREEN}✅ Dockerfile encontrado${NC}"
else
    echo -e "${RED}❌ Dockerfile NÃO encontrado${NC}"
    exit 1
fi

if [ -f "requirements_producao.txt" ]; then
    echo -e "${GREEN}✅ requirements_producao.txt encontrado${NC}"
else
    echo -e "${RED}❌ requirements_producao.txt NÃO encontrado${NC}"
    exit 1
fi

if [ -f "sistema_rural/settings_gcp.py" ]; then
    echo -e "${GREEN}✅ settings_gcp.py encontrado${NC}"
else
    echo -e "${RED}❌ settings_gcp.py NÃO encontrado${NC}"
    exit 1
fi

# Verificar se gcloud está instalado
echo ""
echo "🔧 Verificando gcloud CLI..."
if command -v gcloud &> /dev/null; then
    echo -e "${GREEN}✅ gcloud CLI instalado${NC}"
    gcloud --version | head -n 1
else
    echo -e "${RED}❌ gcloud CLI NÃO encontrado${NC}"
    echo "   Instale: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar autenticação
echo ""
echo "🔐 Verificando autenticação..."
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${GREEN}✅ Autenticado no Google Cloud${NC}"
    gcloud auth list --filter=status:ACTIVE --format="value(account)"
else
    echo -e "${YELLOW}⚠️  Não autenticado - execute: gcloud auth login${NC}"
fi

# Verificar projeto
echo ""
echo "📦 Verificando projeto..."
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -n "$PROJECT" ]; then
    echo -e "${GREEN}✅ Projeto configurado: $PROJECT${NC}"
else
    echo -e "${YELLOW}⚠️  Nenhum projeto configurado${NC}"
    echo "   Configure: gcloud config set project SEU_PROJETO"
fi

# Verificar Python
echo ""
echo "🐍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  Python3 não encontrado${NC}"
fi

# Verificar estrutura Django
echo ""
echo "📋 Verificando estrutura Django..."
if [ -d "sistema_rural" ]; then
    echo -e "${GREEN}✅ Pasta sistema_rural encontrada${NC}"
    
    if [ -f "sistema_rural/settings.py" ]; then
        echo -e "${GREEN}✅ settings.py encontrado${NC}"
    fi
    
    if [ -f "sistema_rural/wsgi.py" ]; then
        echo -e "${GREEN}✅ wsgi.py encontrado${NC}"
    fi
    
    if [ -f "sistema_rural/middleware.py" ]; then
        echo -e "${GREEN}✅ middleware.py encontrado${NC}"
    fi
else
    echo -e "${RED}❌ Pasta sistema_rural NÃO encontrada${NC}"
fi

# Verificar se há arquivos estáticos
echo ""
echo "📦 Verificando arquivos estáticos..."
if [ -d "static" ] || [ -d "gestao_rural/static" ]; then
    echo -e "${GREEN}✅ Pasta static encontrada${NC}"
else
    echo -e "${YELLOW}⚠️  Pasta static não encontrada (pode ser normal)${NC}"
fi

# Resumo
echo ""
echo "=================================="
echo "📊 RESUMO DA VERIFICAÇÃO"
echo "=================================="
echo ""
echo "✅ Arquivos essenciais verificados"
echo "✅ Estrutura Django verificada"
echo ""
echo "🚀 Pronto para deploy!"
echo ""
echo "📖 Próximo passo: Siga o arquivo COMECE_AGORA.md"
echo ""






