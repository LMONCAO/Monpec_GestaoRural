# Script para Corrigir Erro 503 no monpec.com.br
# Conecta via SSH ao servidor e executa diagnóstico e correção

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORREÇÃO ERRO 503 - monpec.com.br" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações SSH
$SSH_KEY = "@MONPEC.key (1-28)"
$SSH_USER = "root"  # Ajuste se necessário
$SSH_HOST = "monpec.com.br"  # Ou IP do servidor (ex: 10.1.1.234)

Write-Host "[INFO] Conectando ao servidor via SSH..." -ForegroundColor Yellow
Write-Host "       Host: $SSH_HOST" -ForegroundColor Gray
Write-Host "       Usuário: $SSH_USER" -ForegroundColor Gray
Write-Host ""

# Verificar se a chave SSH existe
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "[ERRO] Chave SSH não encontrada: $SSH_KEY" -ForegroundColor Red
    Write-Host "[INFO] Verificando chaves SSH alternativas..." -ForegroundColor Yellow
    
    # Tentar encontrar chaves SSH
    $possibleKeys = @(
        "MONPEC.key",
        "monpec.key",
        "$HOME\.ssh\id_rsa",
        "$HOME\.ssh\id_ed25519"
    )
    
    $foundKey = $null
    foreach ($key in $possibleKeys) {
        if (Test-Path $key) {
            $foundKey = $key
            Write-Host "[OK] Usando chave: $key" -ForegroundColor Green
            break
        }
    }
    
    if (-not $foundKey) {
        Write-Host "[ERRO] Nenhuma chave SSH encontrada!" -ForegroundColor Red
        Write-Host "[INFO] Você pode conectar manualmente e executar:" -ForegroundColor Yellow
        Write-Host "       bash /var/www/monpec.com.br/corrigir_503.sh" -ForegroundColor White
        exit 1
    }
    
    $SSH_KEY = $foundKey
}

# Comandos para executar no servidor
$commands = @"
#!/bin/bash
set -e

echo "🔧 DIAGNÓSTICO E CORREÇÃO DO ERRO 503"
echo "====================================="
echo ""

# 1. Verificar status dos serviços
echo "📊 1/12 - Verificando status dos serviços..."
echo ""
echo "=== STATUS MONPEC ==="
systemctl status monpec --no-pager -l | head -20 || echo "Serviço não encontrado"
echo ""

echo "=== STATUS NGINX ==="
systemctl status nginx --no-pager -l | head -20 || echo "Nginx não encontrado"
echo ""

# 2. Verificar se o serviço está rodando
echo "📊 2/12 - Verificando se serviços estão ativos..."
if ! systemctl is-active --quiet monpec 2>/dev/null; then
    echo "❌ Serviço Monpec não está rodando!"
    echo "🚀 Tentando iniciar..."
    systemctl start monpec || true
    sleep 3
    
    if systemctl is-active --quiet monpec; then
        echo "✅ Serviço Monpec iniciado!"
    else
        echo "❌ Falha ao iniciar serviço Monpec"
        echo "📋 Logs de erro:"
        journalctl -u monpec --no-pager -n 30 || true
    fi
else
    echo "✅ Serviço Monpec está rodando!"
fi

if ! systemctl is-active --quiet nginx 2>/dev/null; then
    echo "❌ Nginx não está rodando!"
    echo "🚀 Tentando iniciar..."
    systemctl start nginx || true
    sleep 2
    
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx iniciado!"
    else
        echo "❌ Falha ao iniciar Nginx"
        nginx -t || true
    fi
else
    echo "✅ Nginx está rodando!"
fi
echo ""

# 3. Verificar porta 8000
echo "📊 3/12 - Verificando porta 8000..."
if netstat -tlnp 2>/dev/null | grep -q ":8000" || ss -tlnp 2>/dev/null | grep -q ":8000"; then
    echo "✅ Porta 8000 está em uso!"
    netstat -tlnp 2>/dev/null | grep :8000 || ss -tlnp 2>/dev/null | grep :8000
else
    echo "❌ Porta 8000 não está em uso!"
    echo "⚠️  Gunicorn pode não estar rodando"
fi
echo ""

# 4. Verificar processos Gunicorn
echo "📊 4/12 - Verificando processos Gunicorn..."
GUNICORN_COUNT=\$(ps aux | grep -E '[g]unicorn|python.*wsgi' | wc -l)
if [ "\$GUNICORN_COUNT" -gt 0 ]; then
    echo "✅ Processos Gunicorn encontrados: \$GUNICORN_COUNT"
    ps aux | grep -E '[g]unicorn|python.*wsgi' | grep -v grep | head -5
else
    echo "❌ Nenhum processo Gunicorn encontrado!"
    echo "🚀 Tentando reiniciar serviço..."
    systemctl restart monpec || true
    sleep 5
    
    GUNICORN_COUNT=\$(ps aux | grep -E '[g]unicorn|python.*wsgi' | wc -l)
    if [ "\$GUNICORN_COUNT" -gt 0 ]; then
        echo "✅ Processos Gunicorn iniciados!"
    else
        echo "❌ Falha ao iniciar Gunicorn"
    fi
fi
echo ""

# 5. Verificar logs de erro
echo "📊 5/12 - Verificando logs de erro..."
echo "=== ÚLTIMOS 20 LOGS DO MONPEC ==="
journalctl -u monpec --no-pager -n 20 --no-hostname 2>/dev/null || echo "Logs não disponíveis"
echo ""

echo "=== ÚLTIMOS 10 LOGS DO NGINX ==="
tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo "Arquivo de log não encontrado"
echo ""

# 6. Verificar configuração do Nginx
echo "📊 6/12 - Verificando configuração do Nginx..."
if nginx -t 2>&1 | grep -q "successful"; then
    echo "✅ Configuração do Nginx está correta!"
else
    echo "❌ Erro na configuração do Nginx!"
    nginx -t
fi
echo ""

# 7. Verificar arquivo de configuração do Nginx
echo "📊 7/12 - Verificando configuração do Nginx..."
if [ -f "/etc/nginx/conf.d/monpec.conf" ]; then
    echo "✅ Arquivo de configuração encontrado!"
    echo "Conteúdo:"
    cat /etc/nginx/conf.d/monpec.conf | head -30
elif [ -f "/etc/nginx/sites-available/monpec.com.br" ]; then
    echo "✅ Arquivo de configuração encontrado!"
    echo "Conteúdo:"
    cat /etc/nginx/sites-available/monpec.com.br | head -30
else
    echo "⚠️  Arquivo de configuração não encontrado!"
    echo "Arquivos disponíveis:"
    ls -la /etc/nginx/conf.d/ 2>/dev/null || ls -la /etc/nginx/sites-available/ 2>/dev/null || echo "Diretório não encontrado"
fi
echo ""

# 8. Testar conectividade local
echo "📊 8/12 - Testando conectividade local..."
HTTP_STATUS=\$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000 2>/dev/null || echo "000")
if [ "\$HTTP_STATUS" = "200" ] || [ "\$HTTP_STATUS" = "302" ] || [ "\$HTTP_STATUS" = "301" ]; then
    echo "✅ Backend respondendo! (HTTP \$HTTP_STATUS)"
else
    echo "❌ Backend não está respondendo! (HTTP \$HTTP_STATUS)"
    echo "⚠️  Isso pode ser a causa do erro 503"
fi
echo ""

# 9. Verificar ambiente virtual e Gunicorn
echo "📊 9/12 - Verificando ambiente virtual..."
if [ -f "/var/www/monpec.com.br/venv/bin/gunicorn" ]; then
    echo "✅ Gunicorn encontrado!"
else
    echo "❌ Gunicorn não encontrado!"
    echo "⚠️  Caminho esperado: /var/www/monpec.com.br/venv/bin/gunicorn"
fi

if [ -f "/var/www/monpec.com.br/sistema_rural/settings_producao.py" ]; then
    echo "✅ settings_producao.py encontrado!"
else
    echo "❌ settings_producao.py não encontrado!"
fi
echo ""

# 10. Verificar banco de dados
echo "📊 10/12 - Verificando conexão com banco de dados..."
cd /var/www/monpec.com.br 2>/dev/null || echo "⚠️  Diretório não encontrado"
if [ -d "/var/www/monpec.com.br" ]; then
    cd /var/www/monpec.com.br
    source venv/bin/activate 2>/dev/null || true
    python manage.py check --settings=sistema_rural.settings_producao 2>&1 | head -10 || echo "⚠️  Erro ao verificar configuração"
fi
echo ""

# 11. Reiniciar serviços
echo "📊 11/12 - Reiniciando serviços..."
systemctl daemon-reload
systemctl restart monpec || true
sleep 5
systemctl restart nginx || true
sleep 2
echo ""

# 12. Verificação final
echo "📊 12/12 - Verificação final..."
echo ""

if systemctl is-active --quiet monpec && systemctl is-active --quiet nginx; then
    echo "✅ Ambos os serviços estão rodando!"
    
    sleep 5
    HTTP_STATUS=\$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://127.0.0.1:8000 2>/dev/null || echo "000")
    
    if [ "\$HTTP_STATUS" = "200" ] || [ "\$HTTP_STATUS" = "302" ] || [ "\$HTTP_STATUS" = "301" ]; then
        echo ""
        echo "✅✅✅ SISTEMA CORRIGIDO E FUNCIONANDO! ✅✅✅"
        echo ""
        echo "🌐 Teste acessando: https://monpec.com.br"
    else
        echo "⚠️  Serviços rodando, mas backend ainda não responde corretamente"
        echo "📋 Verifique logs: journalctl -u monpec -n 50"
    fi
else
    echo "❌ Ainda há problemas com os serviços!"
    echo ""
    echo "📊 STATUS ATUAL:"
    systemctl status monpec --no-pager -l | head -15 || true
    echo ""
    systemctl status nginx --no-pager -l | head -15 || true
fi

echo ""
echo "======================================"
echo "🔍 DIAGNÓSTICO CONCLUÍDO!"
echo "======================================"
"@

# Tentar executar via SSH
Write-Host "[INFO] Executando diagnóstico e correção no servidor..." -ForegroundColor Cyan
Write-Host ""

try {
    # Tentar com chave SSH específica
    if (Test-Path $SSH_KEY) {
        $sshCmd = "ssh -i `"$SSH_KEY`" -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST"
    } else {
        $sshCmd = "ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST"
    }
    
    # Executar comandos
    $commands | & $sshCmd.Split(' ') | ForEach-Object {
        Write-Host $_ -ForegroundColor $(if ($_ -match '✅|SUCESSO|FUNCIONANDO') { 'Green' } 
                                         elseif ($_ -match '❌|ERRO|Falha') { 'Red' } 
                                         elseif ($_ -match '⚠️|AVISO') { 'Yellow' } 
                                         else { 'White' })
    }
    
    Write-Host ""
    Write-Host "[OK] Diagnóstico concluído!" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "[ERRO] Falha ao conectar via SSH: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "[INFO] Você pode executar manualmente no servidor:" -ForegroundColor Yellow
    Write-Host "       1. Conecte via SSH ao servidor" -ForegroundColor White
    Write-Host "       2. Execute: bash /var/www/monpec.com.br/corrigir_503.sh" -ForegroundColor White
    Write-Host "       3. Ou execute os comandos acima manualmente" -ForegroundColor White
    Write-Host ""
    Write-Host "[INFO] Comandos úteis para diagnóstico manual:" -ForegroundColor Yellow
    Write-Host "       - Ver status: systemctl status monpec" -ForegroundColor White
    Write-Host "       - Ver logs: journalctl -u monpec -f" -ForegroundColor White
    Write-Host "       - Reiniciar: systemctl restart monpec && systemctl restart nginx" -ForegroundColor White
    Write-Host "       - Testar local: curl -I http://127.0.0.1:8000" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FIM DO DIAGNÓSTICO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
















