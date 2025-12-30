#!/bin/bash
# 🔍 AUDITORIA COMPLETA DO PROJETO PARA DEPLOY
# Verifica todos os aspectos do projeto antes do deploy

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  AUDITORIA COMPLETA DO PROJETO${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Função para verificar
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
    else
        echo -e "${RED}❌ $1${NC}"
        ((ERRORS++))
    fi
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ==========================================
# 1. VERIFICAR ESTRUTURA DE ARQUIVOS
# ==========================================
echo -e "${CYAN}[1/10] Verificando estrutura de arquivos...${NC}"

[ -f "manage.py" ] && check "manage.py existe" || warn "manage.py não encontrado"
[ -f "Dockerfile.prod" ] && check "Dockerfile.prod existe" || warn "Dockerfile.prod não encontrado"
[ -f "requirements_producao.txt" ] && check "requirements_producao.txt existe" || warn "requirements_producao.txt não encontrado"
[ -f "sistema_rural/settings_gcp.py" ] && check "settings_gcp.py existe" || warn "settings_gcp.py não encontrado"
[ -f "sistema_rural/wsgi.py" ] && check "wsgi.py existe" || warn "wsgi.py não encontrado"
[ -d "gestao_rural" ] && check "gestao_rural/ existe" || warn "gestao_rural/ não encontrado"
[ -d "templates" ] && check "templates/ existe" || warn "templates/ não encontrado"
[ -d "static" ] && check "static/ existe" || warn "static/ não encontrado"

echo ""

# ==========================================
# 2. VERIFICAR REQUIREMENTS
# ==========================================
echo -e "${CYAN}[2/10] Verificando requirements_producao.txt...${NC}"

if [ -f "requirements_producao.txt" ]; then
    # Verificar linhas duplicadas
    DUPLICATES=$(sort requirements_producao.txt | uniq -d)
    if [ -z "$DUPLICATES" ]; then
        check "Sem linhas duplicadas"
    else
        warn "Linhas duplicadas encontradas:"
        echo "$DUPLICATES"
    fi
    
    # Verificar se openpyxl está presente
    if grep -q "openpyxl" requirements_producao.txt; then
        check "openpyxl está presente"
    else
        warn "openpyxl não encontrado (necessário para exportação Excel)"
    fi
    
    # Verificar se gunicorn está presente
    if grep -q "gunicorn" requirements_producao.txt; then
        check "gunicorn está presente"
    else
        warn "gunicorn não encontrado (necessário para produção)"
    fi
    
    # Verificar se psycopg2 está presente
    if grep -q "psycopg2" requirements_producao.txt; then
        check "psycopg2 está presente"
    else
        warn "psycopg2 não encontrado (necessário para PostgreSQL)"
    fi
else
    warn "requirements_producao.txt não encontrado"
fi

echo ""

# ==========================================
# 3. VERIFICAR DOCKERFILE
# ==========================================
echo -e "${CYAN}[3/10] Verificando Dockerfile.prod...${NC}"

if [ -f "Dockerfile.prod" ]; then
    # Verificar se usa Python 3.11
    if grep -q "python:3.11" Dockerfile.prod; then
        check "Usa Python 3.11"
    else
        warn "Não usa Python 3.11 (pode causar problemas)"
    fi
    
    # Verificar se copia requirements
    if grep -q "requirements_producao.txt" Dockerfile.prod; then
        check "Copia requirements_producao.txt"
    else
        warn "Não copia requirements_producao.txt"
    fi
    
    # Verificar se expõe porta 8080
    if grep -q "EXPOSE 8080" Dockerfile.prod || grep -q "PORT=8080" Dockerfile.prod; then
        check "Porta 8080 configurada"
    else
        warn "Porta 8080 não configurada"
    fi
    
    # Verificar se usa gunicorn
    if grep -q "gunicorn" Dockerfile.prod; then
        check "Usa gunicorn"
    else
        warn "Não usa gunicorn"
    fi
else
    warn "Dockerfile.prod não encontrado"
fi

echo ""

# ==========================================
# 4. VERIFICAR SETTINGS_GCP
# ==========================================
echo -e "${CYAN}[4/10] Verificando settings_gcp.py...${NC}"

if [ -f "sistema_rural/settings_gcp.py" ]; then
    # Verificar se configura Cloud SQL
    if grep -q "CLOUD_SQL_CONNECTION_NAME" sistema_rural/settings_gcp.py; then
        check "Configura Cloud SQL"
    else
        warn "Não configura Cloud SQL"
    fi
    
    # Verificar se configura ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS" sistema_rural/settings_gcp.py; then
        check "Configura ALLOWED_HOSTS"
    else
        warn "Não configura ALLOWED_HOSTS"
    fi
    
    # Verificar se usa settings.py como base
    if grep -q "from .settings import" sistema_rural/settings_gcp.py; then
        check "Herda de settings.py"
    else
        warn "Não herda de settings.py"
    fi
else
    warn "settings_gcp.py não encontrado"
fi

echo ""

# ==========================================
# 5. VERIFICAR WSGI
# ==========================================
echo -e "${CYAN}[5/10] Verificando wsgi.py...${NC}"

if [ -f "sistema_rural/wsgi.py" ]; then
    # Verificar se detecta Cloud Run
    if grep -q "K_SERVICE" sistema_rural/wsgi.py || grep -q "settings_gcp" sistema_rural/wsgi.py; then
        check "Detecta ambiente Cloud Run"
    else
        warn "Não detecta ambiente Cloud Run"
    fi
else
    warn "wsgi.py não encontrado"
fi

echo ""

# ==========================================
# 6. VERIFICAR ARQUIVOS ESTÁTICOS
# ==========================================
echo -e "${CYAN}[6/10] Verificando arquivos estáticos...${NC}"

if [ -d "static" ]; then
    STATIC_COUNT=$(find static -type f | wc -l)
    info "Encontrados $STATIC_COUNT arquivos estáticos"
    
    if [ $STATIC_COUNT -gt 0 ]; then
        check "Arquivos estáticos presentes"
    else
        warn "Pasta static está vazia"
    fi
else
    warn "Pasta static não encontrada"
fi

echo ""

# ==========================================
# 7. VERIFICAR TEMPLATES
# ==========================================
echo -e "${CYAN}[7/10] Verificando templates...${NC}"

if [ -d "templates" ]; then
    TEMPLATE_COUNT=$(find templates -name "*.html" | wc -l)
    info "Encontrados $TEMPLATE_COUNT templates HTML"
    
    if [ $TEMPLATE_COUNT -gt 0 ]; then
        check "Templates presentes"
    else
        warn "Nenhum template HTML encontrado"
    fi
else
    warn "Pasta templates não encontrada"
fi

echo ""

# ==========================================
# 8. VERIFICAR GOOGLE CLOUD SDK
# ==========================================
echo -e "${CYAN}[8/10] Verificando Google Cloud SDK...${NC}"

if command -v gcloud &> /dev/null; then
    check "gcloud CLI instalado"
    GCLOUD_VERSION=$(gcloud --version | head -n 1)
    info "Versão: $GCLOUD_VERSION"
    
    # Verificar autenticação
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        check "Autenticado no Google Cloud"
        ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
        info "Conta: $ACCOUNT"
    else
        warn "Não autenticado no Google Cloud"
    fi
    
    # Verificar projeto configurado
    PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ ! -z "$PROJECT" ]; then
        check "Projeto configurado: $PROJECT"
    else
        warn "Projeto não configurado"
    fi
else
    warn "gcloud CLI não instalado"
fi

echo ""

# ==========================================
# 9. VERIFICAR ESTRUTURA DO PROJETO DJANGO
# ==========================================
echo -e "${CYAN}[9/10] Verificando estrutura Django...${NC}"

if [ -f "manage.py" ]; then
    # Verificar se consegue importar Django
    if python3 -c "import django; print(django.get_version())" 2>/dev/null; then
        DJANGO_VERSION=$(python3 -c "import django; print(django.get_version())" 2>/dev/null)
        check "Django instalado: $DJANGO_VERSION"
    else
        warn "Django não instalado ou não acessível"
    fi
    
    # Verificar apps instalados
    if [ -d "gestao_rural" ]; then
        if [ -f "gestao_rural/apps.py" ] || [ -f "gestao_rural/__init__.py" ]; then
            check "App gestao_rural configurado"
        else
            warn "App gestao_rural não configurado corretamente"
        fi
    fi
else
    warn "manage.py não encontrado"
fi

echo ""

# ==========================================
# 10. VERIFICAR CONFIGURAÇÕES DE DEPLOY
# ==========================================
echo -e "${CYAN}[10/10] Verificando configurações de deploy...${NC}"

# Verificar variáveis de ambiente necessárias
REQUIRED_VARS=("PROJECT_ID" "SERVICE_NAME" "REGION" "DB_INSTANCE")
for VAR in "${REQUIRED_VARS[@]}"; do
    if grep -r "$VAR" *.bat *.sh *.md 2>/dev/null | grep -q "="; then
        check "$VAR está configurado nos scripts"
    else
        warn "$VAR não encontrado nos scripts"
    fi
done

echo ""

# ==========================================
# RESUMO FINAL
# ==========================================
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  RESUMO DA AUDITORIA${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Projeto está pronto para deploy!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Projeto tem $WARNINGS avisos, mas pode fazer deploy${NC}"
    exit 0
else
    echo -e "${RED}❌ Projeto tem $ERRORS erros e $WARNINGS avisos${NC}"
    echo -e "${RED}Corrija os erros antes de fazer deploy${NC}"
    exit 1
fi

