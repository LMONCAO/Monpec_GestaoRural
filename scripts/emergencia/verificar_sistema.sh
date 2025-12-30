#!/bin/bash
# Script para verificar saúde do sistema após deploy
# Uso: ./scripts/emergencia/verificar_sistema.sh

echo "🔍 Verificando saúde do sistema..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERROS=0

# 1. Verificar se Django está configurado
echo "1️⃣ Verificando configuração do Django..."
python manage.py check --deploy > /tmp/django_check.log 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Django OK${NC}"
else
    echo -e "${RED}❌ Erros no Django:${NC}"
    cat /tmp/django_check.log
    ERROS=$((ERROS + 1))
fi

# 2. Verificar migrações
echo ""
echo "2️⃣ Verificando migrações..."
python manage.py showmigrations --list | grep "\[ \]" > /tmp/migrations_pendentes.log
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}⚠️ Migrações pendentes:${NC}"
    cat /tmp/migrations_pendentes.log
else
    echo -e "${GREEN}✅ Todas as migrações aplicadas${NC}"
fi

# 3. Verificar banco de dados
echo ""
echo "3️⃣ Verificando conexão com banco de dados..."
python manage.py dbshell --command "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Conexão com banco OK${NC}"
else
    echo -e "${RED}❌ Erro ao conectar com banco de dados${NC}"
    ERROS=$((ERROS + 1))
fi

# 4. Verificar arquivos estáticos
echo ""
echo "4️⃣ Verificando arquivos estáticos..."
if [ -d "staticfiles" ] && [ "$(ls -A staticfiles)" ]; then
    echo -e "${GREEN}✅ Arquivos estáticos presentes${NC}"
else
    echo -e "${YELLOW}⚠️ Arquivos estáticos não encontrados (pode ser normal se não coletados)${NC}"
fi

# 5. Verificar logs recentes por erros
echo ""
echo "5️⃣ Verificando logs recentes..."
if [ -f "logs/django.log" ]; then
    ULTIMOS_ERROS=$(tail -100 logs/django.log | grep -i "error\|exception\|traceback" | tail -5)
    if [ -n "$ULTIMOS_ERROS" ]; then
        echo -e "${YELLOW}⚠️ Últimos erros nos logs:${NC}"
        echo "$ULTIMOS_ERROS"
    else
        echo -e "${GREEN}✅ Nenhum erro recente nos logs${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Arquivo de log não encontrado${NC}"
fi

# 6. Verificar espaço em disco
echo ""
echo "6️⃣ Verificando espaço em disco..."
ESPACO=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$ESPACO" -lt 80 ]; then
    echo -e "${GREEN}✅ Espaço em disco OK (${ESPACO}% usado)${NC}"
elif [ "$ESPACO" -lt 90 ]; then
    echo -e "${YELLOW}⚠️ Espaço em disco: ${ESPACO}% usado${NC}"
else
    echo -e "${RED}❌ Espaço em disco crítico: ${ESPACO}% usado${NC}"
    ERROS=$((ERROS + 1))
fi

# Resumo
echo ""
echo "=========================================="
if [ $ERROS -eq 0 ]; then
    echo -e "${GREEN}✅ Sistema OK - Nenhum erro crítico encontrado${NC}"
    exit 0
else
    echo -e "${RED}❌ Sistema com problemas - $ERROS erro(s) encontrado(s)${NC}"
    exit 1
fi






