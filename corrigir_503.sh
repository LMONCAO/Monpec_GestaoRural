#!/bin/bash
# 🔧 CORREÇÃO DO ERRO 503 - MONPEC.COM.BR

echo "🔧 CORRIGINDO ERRO 503 - MONPEC.COM.BR"
echo "======================================"
echo ""

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

# 1. VERIFICAR STATUS DOS SERVIÇOS
log "Verificando status dos serviços..."
echo ""

echo "=== STATUS MONPEC ==="
systemctl status monpec --no-pager -l | head -20
echo ""

echo "=== STATUS NGINX ==="
systemctl status nginx --no-pager -l | head -20
echo ""

# 2. VERIFICAR SE O SERVIÇO ESTÁ RODANDO
if ! systemctl is-active --quiet monpec; then
    error "Serviço Monpec não está rodando!"
    log "Tentando iniciar o serviço..."
    systemctl start monpec
    sleep 3
    
    if systemctl is-active --quiet monpec; then
        success "Serviço Monpec iniciado com sucesso!"
    else
        error "Falha ao iniciar o serviço Monpec!"
        log "Verificando logs de erro..."
        journalctl -u monpec --no-pager -n 30
        echo ""
    fi
else
    success "Serviço Monpec está rodando!"
fi

# 3. VERIFICAR NGINX
if ! systemctl is-active --quiet nginx; then
    error "Nginx não está rodando!"
    log "Iniciando Nginx..."
    systemctl start nginx
    sleep 2
    
    if systemctl is-active --quiet nginx; then
        success "Nginx iniciado com sucesso!"
    else
        error "Falha ao iniciar Nginx!"
        log "Verificando configuração do Nginx..."
        nginx -t
    fi
else
    success "Nginx está rodando!"
fi

# 4. VERIFICAR PORTA 8000
log "Verificando porta 8000..."
if netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    success "Porta 8000 está em uso!"
    netstat -tlnp | grep :8000
else
    error "Porta 8000 não está em uso!"
    warning "O Gunicorn pode não estar rodando corretamente"
fi
echo ""

# 5. VERIFICAR PROCESSOS GUNICORN
log "Verificando processos Gunicorn..."
GUNICORN_PROCESSES=$(ps aux | grep gunicorn | grep -v grep | wc -l)
if [ "$GUNICORN_PROCESSES" -gt 0 ]; then
    success "Processos Gunicorn encontrados: $GUNICORN_PROCESSES"
    ps aux | grep gunicorn | grep -v grep
else
    error "Nenhum processo Gunicorn encontrado!"
    warning "Tentando reiniciar o serviço..."
    systemctl restart monpec
    sleep 5
    
    GUNICORN_PROCESSES=$(ps aux | grep gunicorn | grep -v grep | wc -l)
    if [ "$GUNICORN_PROCESSES" -gt 0 ]; then
        success "Processos Gunicorn iniciados após reinício!"
    else
        error "Falha ao iniciar processos Gunicorn!"
    fi
fi
echo ""

# 6. VERIFICAR LOGS DE ERRO
log "Verificando logs de erro recentes..."
echo "=== ÚLTIMOS 20 LOGS DO MONPEC ==="
journalctl -u monpec --no-pager -n 20 --no-hostname
echo ""

echo "=== ÚLTIMOS 10 LOGS DO NGINX ==="
tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo "Arquivo de log não encontrado"
echo ""

# 7. VERIFICAR CONFIGURAÇÃO DO NGINX
log "Verificando configuração do Nginx..."
if nginx -t 2>&1 | grep -q "successful"; then
    success "Configuração do Nginx está correta!"
else
    error "Erro na configuração do Nginx!"
    nginx -t
    echo ""
fi

# 8. VERIFICAR ARQUIVO DE CONFIGURAÇÃO DO NGINX
log "Verificando arquivo de configuração do Nginx..."
if [ -f "/etc/nginx/conf.d/monpec.conf" ]; then
    success "Arquivo de configuração encontrado!"
    echo "Conteúdo do arquivo:"
    cat /etc/nginx/conf.d/monpec.conf
else
    warning "Arquivo /etc/nginx/conf.d/monpec.conf não encontrado!"
    log "Verificando outros arquivos de configuração..."
    ls -la /etc/nginx/conf.d/
fi
echo ""

# 9. TESTAR CONECTIVIDADE LOCAL
log "Testando conectividade local na porta 8000..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000 2>/dev/null)
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
    success "Backend respondendo corretamente! (HTTP $HTTP_STATUS)"
else
    error "Backend não está respondendo corretamente! (HTTP $HTTP_STATUS)"
    warning "Isso pode ser a causa do erro 503"
fi
echo ""

# 10. VERIFICAR AMBIENTE VIRTUAL E GUNICORN
log "Verificando ambiente virtual e Gunicorn..."
if [ -f "/var/www/monpec.com.br/venv/bin/gunicorn" ]; then
    success "Gunicorn encontrado no ambiente virtual!"
else
    error "Gunicorn não encontrado no ambiente virtual!"
    warning "Caminho esperado: /var/www/monpec.com.br/venv/bin/gunicorn"
fi

if [ -f "/var/www/monpec.com.br/sistema_rural/settings_producao.py" ]; then
    success "Arquivo settings_producao.py encontrado!"
else
    error "Arquivo settings_producao.py não encontrado!"
fi
echo ""

# 11. TENTAR REINICIAR SERVIÇOS
log "Reiniciando serviços para garantir que estão funcionando..."
systemctl daemon-reload
systemctl restart monpec
sleep 5
systemctl restart nginx
sleep 2
echo ""

# 12. VERIFICAÇÃO FINAL
log "Verificação final..."
echo ""

if systemctl is-active --quiet monpec && systemctl is-active --quiet nginx; then
    success "Ambos os serviços estão rodando!"
    
    # Aguardar um pouco e testar novamente
    sleep 5
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000 2>/dev/null)
    
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
        success "✅ SISTEMA CORRIGIDO E FUNCIONANDO!"
        echo ""
        echo "🌐 Teste acessando: http://monpec.com.br"
        echo "📊 Status: systemctl status monpec"
        echo "📝 Logs: journalctl -u monpec -f"
    else
        warning "Serviços estão rodando, mas backend ainda não responde corretamente"
        echo "Verifique os logs para mais detalhes: journalctl -u monpec -n 50"
    fi
else
    error "Ainda há problemas com os serviços!"
    echo ""
    echo "📊 STATUS ATUAL:"
    systemctl status monpec --no-pager -l | head -15
    echo ""
    systemctl status nginx --no-pager -l | head -15
fi

echo ""
echo "======================================"
echo "🔍 DIAGNÓSTICO CONCLUÍDO!"
echo "======================================"
echo ""
echo "💡 Comandos úteis:"
echo "   - Ver status: systemctl status monpec"
echo "   - Ver logs: journalctl -u monpec -f"
echo "   - Reiniciar: systemctl restart monpec && systemctl restart nginx"
echo "   - Testar local: curl -I http://127.0.0.1:8000"
echo ""




