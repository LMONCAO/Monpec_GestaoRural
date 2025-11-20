#!/bin/bash
# 🔍 DIAGNÓSTICO COMPLETO DO SISTEMA MONPEC

echo "🔍 DIAGNÓSTICO DO SISTEMA MONPEC"
echo "================================="

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# 1. VERIFICAR SISTEMA
log "Verificando sistema..."
echo "Sistema: $(uname -a)"
echo "Data: $(date)"
echo "Uptime: $(uptime)"

# 2. VERIFICAR PROCESSOS
log "Verificando processos..."
echo "=== PROCESSOS PYTHON ==="
ps aux | grep python | grep -v grep
echo ""
echo "=== PROCESSOS NGINX ==="
ps aux | grep nginx | grep -v grep
echo ""
echo "=== PROCESSOS GUNICORN ==="
ps aux | grep gunicorn | grep -v grep

# 3. VERIFICAR PORTAS
log "Verificando portas..."
echo "=== PORTA 80 ==="
netstat -tlnp | grep :80
echo ""
echo "=== PORTA 8000 ==="
netstat -tlnp | grep :8000
echo ""
echo "=== TODAS AS PORTAS ATIVAS ==="
netstat -tlnp | grep LISTEN

# 4. VERIFICAR SERVIÇOS
log "Verificando serviços..."
echo "=== STATUS MONPEC ==="
systemctl status monpec --no-pager
echo ""
echo "=== STATUS NGINX ==="
systemctl status nginx --no-pager
echo ""
echo "=== STATUS POSTGRESQL ==="
systemctl status postgresql --no-pager

# 5. VERIFICAR ARQUIVOS
log "Verificando arquivos..."
echo "=== DIRETÓRIO DO PROJETO ==="
ls -la /var/www/monpec.com.br/
echo ""
echo "=== ARQUIVO GUNICORN ==="
ls -la /var/www/monpec.com.br/venv/bin/gunicorn
echo ""
echo "=== ARQUIVO SETTINGS ==="
ls -la /var/www/monpec.com.br/sistema_rural/settings_producao.py

# 6. VERIFICAR LOGS
log "Verificando logs..."
echo "=== LOGS MONPEC ==="
journalctl -u monpec --no-pager -n 10
echo ""
echo "=== LOGS NGINX ==="
tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo "Arquivo de log não encontrado"

# 7. TESTAR CONEXÕES
log "Testando conexões..."
echo "=== TESTE LOCALHOST:8000 ==="
curl -I http://localhost:8000 2>/dev/null || echo "Falha na conexão"
echo ""
echo "=== TESTE LOCALHOST:80 ==="
curl -I http://localhost:80 2>/dev/null || echo "Falha na conexão"

# 8. VERIFICAR FIREWALL
log "Verificando firewall..."
echo "=== STATUS FIREWALL ==="
firewall-cmd --list-all 2>/dev/null || echo "Firewall não configurado"

# 9. VERIFICAR BANCO DE DADOS
log "Verificando banco de dados..."
echo "=== CONEXÃO POSTGRESQL ==="
sudo -u postgres psql -c "SELECT version();" 2>/dev/null || echo "Falha na conexão com PostgreSQL"

# 10. VERIFICAR AMBIENTE VIRTUAL
log "Verificando ambiente virtual..."
echo "=== PYTHON VERSION ==="
/var/www/monpec.com.br/venv/bin/python --version
echo ""
echo "=== PIP LIST ==="
/var/www/monpec.com.br/venv/bin/pip list | grep -E "(django|gunicorn)"

# 11. TESTAR DJANGO
log "Testando Django..."
cd /var/www/monpec.com.br
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
echo "=== DJANGO CHECK ==="
python manage.py check 2>&1 || echo "Falha no check do Django"

echo ""
echo "🎯 DIAGNÓSTICO CONCLUÍDO!"
echo "========================="
echo "Verifique os resultados acima para identificar problemas."

