#!/bin/bash
# Script rápido de verificação do sistema
# Execute para verificar se tudo está funcionando

echo "========================================"
echo "VERIFICAÇÃO RÁPIDA - SISTEMA MONPEC"
echo "========================================"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
        return 0
    else
        echo -e "${RED}✗ $1${NC}"
        return 1
    fi
}

# 1. Verificar Python
echo "1. Verificando Python..."
python --version > /dev/null 2>&1
check "Python instalado"

# 2. Verificar Django
echo "2. Verificando Django..."
python -c "import django" > /dev/null 2>&1
check "Django instalado"

# 3. Verificar arquivo .env_producao
echo "3. Verificando .env_producao..."
[ -f ".env_producao" ] && check ".env_producao existe" || echo -e "${RED}✗ .env_producao não encontrado${NC}"

# 4. Verificar configurações Django
echo "4. Verificando configurações Django..."
python manage.py check --settings=sistema_rural.settings_producao > /dev/null 2>&1
check "Configurações Django OK"

# 5. Verificar banco de dados
echo "5. Verificando banco de dados..."
python manage.py dbshell --settings=sistema_rural.settings_producao -c "SELECT 1;" > /dev/null 2>&1
check "Conexão com banco de dados OK"

# 6. Verificar migrações
echo "6. Verificando migrações..."
pending=$(python manage.py showmigrations --settings=sistema_rural.settings_producao 2>/dev/null | grep -c "\[ \]")
if [ "$pending" -eq 0 ]; then
    check "Nenhuma migração pendente"
else
    echo -e "${YELLOW}⚠ $pending migração(ões) pendente(s)${NC}"
fi

# 7. Verificar arquivos estáticos
echo "7. Verificando arquivos estáticos..."
[ -d "staticfiles" ] && [ "$(ls -A staticfiles 2>/dev/null)" ] && check "Arquivos estáticos coletados" || echo -e "${YELLOW}⚠ Arquivos estáticos não coletados${NC}"

# 8. Verificar WSGI
echo "8. Verificando WSGI..."
python -c "from sistema_rural import wsgi" > /dev/null 2>&1
check "WSGI configurado corretamente"

# 9. Verificar logs
echo "9. Verificando logs..."
if [ -f "/var/log/monpec/django.log" ] || [ -f "logs/django.log" ]; then
    check "Arquivo de log existe"
else
    echo -e "${YELLOW}⚠ Arquivo de log não encontrado${NC}"
fi

echo ""
echo "========================================"
echo "VERIFICAÇÃO CONCLUÍDA"
echo "========================================"









