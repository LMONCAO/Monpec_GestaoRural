#!/bin/bash
# 🔍 Script de Diagnóstico e Correção: Service Unavailable (503)

echo "=========================================="
echo "🔍 DIAGNÓSTICO: Service Unavailable (503)"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar status do serviço Gunicorn
echo "1️⃣ Verificando status do serviço Gunicorn..."
if systemctl is-active --quiet sistema-rural; then
    echo -e "${GREEN}✅ Serviço sistema-rural está rodando${NC}"
else
    echo -e "${RED}❌ Serviço sistema-rural NÃO está rodando${NC}"
    echo "Tentando iniciar..."
    sudo systemctl start sistema-rural
    sleep 2
    if systemctl is-active --quiet sistema-rural; then
        echo -e "${GREEN}✅ Serviço iniciado com sucesso${NC}"
    else
        echo -e "${RED}❌ Falha ao iniciar serviço${NC}"
    fi
fi
echo ""

# 2. Verificar status do Nginx
echo "2️⃣ Verificando status do Nginx..."
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx está rodando${NC}"
else
    echo -e "${RED}❌ Nginx NÃO está rodando${NC}"
    echo "Tentando iniciar..."
    sudo systemctl start nginx
    sleep 2
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx iniciado com sucesso${NC}"
    else
        echo -e "${RED}❌ Falha ao iniciar Nginx${NC}"
    fi
fi
echo ""

# 3. Verificar se o socket existe
echo "3️⃣ Verificando socket Unix..."
SOCKET_PATH="/home/django/sistema-rural/sistema_rural.sock"
if [ -S "$SOCKET_PATH" ]; then
    echo -e "${GREEN}✅ Socket existe: $SOCKET_PATH${NC}"
    ls -la "$SOCKET_PATH"
    
    # Verificar permissões
    SOCKET_OWNER=$(stat -c '%U:%G' "$SOCKET_PATH")
    if [ "$SOCKET_OWNER" != "django:www-data" ]; then
        echo -e "${YELLOW}⚠️ Permissões incorretas. Corrigindo...${NC}"
        sudo chown django:www-data "$SOCKET_PATH"
        sudo chmod 660 "$SOCKET_PATH"
        echo -e "${GREEN}✅ Permissões corrigidas${NC}"
    else
        echo -e "${GREEN}✅ Permissões corretas${NC}"
    fi
else
    echo -e "${RED}❌ Socket NÃO existe: $SOCKET_PATH${NC}"
    echo "Isso geralmente significa que o Gunicorn não está rodando corretamente."
    echo "Verificando logs..."
fi
echo ""

# 4. Verificar processos Gunicorn
echo "4️⃣ Verificando processos Gunicorn..."
GUNICORN_PROCESSES=$(ps aux | grep gunicorn | grep -v grep | wc -l)
if [ "$GUNICORN_PROCESSES" -gt 0 ]; then
    echo -e "${GREEN}✅ Encontrados $GUNICORN_PROCESSES processo(s) Gunicorn${NC}"
    ps aux | grep gunicorn | grep -v grep
else
    echo -e "${RED}❌ Nenhum processo Gunicorn encontrado${NC}"
fi
echo ""

# 5. Verificar logs recentes do Gunicorn
echo "5️⃣ Últimas 20 linhas dos logs do Gunicorn:"
echo "----------------------------------------"
journalctl -u sistema-rural -n 20 --no-pager | tail -n 20
echo ""

# 6. Verificar logs do Nginx
echo "6️⃣ Últimas 20 linhas dos logs de erro do Nginx:"
echo "----------------------------------------"
if [ -f /var/log/nginx/error.log ]; then
    tail -n 20 /var/log/nginx/error.log
else
    echo "Arquivo de log não encontrado"
fi
echo ""

# 7. Testar configuração do Nginx
echo "7️⃣ Testando configuração do Nginx..."
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✅ Configuração do Nginx está correta${NC}"
else
    echo -e "${RED}❌ Erro na configuração do Nginx${NC}"
    sudo nginx -t
fi
echo ""

# 8. Tentar correção automática
echo "8️⃣ Tentando correção automática..."
echo "----------------------------------------"

# Parar serviços
echo "Parando serviços..."
sudo systemctl stop sistema-rural 2>/dev/null
sudo systemctl stop nginx 2>/dev/null
sleep 1

# Remover socket antigo
if [ -S "$SOCKET_PATH" ]; then
    echo "Removendo socket antigo..."
    sudo rm -f "$SOCKET_PATH"
fi

# Corrigir permissões do diretório
echo "Corrigindo permissões..."
sudo chown -R django:www-data /home/django/sistema-rural 2>/dev/null
sudo chmod 755 /home/django/sistema-rural 2>/dev/null

# Recarregar systemd
echo "Recarregando systemd..."
sudo systemctl daemon-reload

# Iniciar Gunicorn
echo "Iniciando Gunicorn..."
sudo systemctl start sistema-rural
sleep 3

# Verificar se o socket foi criado
if [ -S "$SOCKET_PATH" ]; then
    echo -e "${GREEN}✅ Socket criado com sucesso${NC}"
    ls -la "$SOCKET_PATH"
    sudo chown django:www-data "$SOCKET_PATH"
    sudo chmod 660 "$SOCKET_PATH"
else
    echo -e "${RED}❌ Socket não foi criado${NC}"
    echo "Verifique os logs do Gunicorn para mais detalhes:"
    journalctl -u sistema-rural -n 30 --no-pager
fi

# Iniciar Nginx
echo "Iniciando Nginx..."
sudo systemctl start nginx
sleep 1

echo ""
echo "=========================================="
echo "📊 STATUS FINAL"
echo "=========================================="

# Status final
if systemctl is-active --quiet sistema-rural; then
    echo -e "${GREEN}✅ sistema-rural: ATIVO${NC}"
else
    echo -e "${RED}❌ sistema-rural: INATIVO${NC}"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ nginx: ATIVO${NC}"
else
    echo -e "${RED}❌ nginx: INATIVO${NC}"
fi

if [ -S "$SOCKET_PATH" ]; then
    echo -e "${GREEN}✅ Socket: EXISTE${NC}"
else
    echo -e "${RED}❌ Socket: NÃO EXISTE${NC}"
fi

echo ""
echo "=========================================="
echo "📋 PRÓXIMOS PASSOS"
echo "=========================================="
echo ""
echo "Se o problema persistir:"
echo "1. Verifique os logs completos: journalctl -u sistema-rural -f"
echo "2. Verifique os logs do Nginx: tail -f /var/log/nginx/error.log"
echo "3. Teste a aplicação diretamente:"
echo "   sudo -u django bash -c 'cd /home/django/sistema-rural && source venv/bin/activate && gunicorn --bind 127.0.0.1:8000 sistema_rural.wsgi:application'"
echo "4. Verifique recursos do servidor: free -h && df -h"
echo ""
