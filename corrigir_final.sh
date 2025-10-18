#!/bin/bash
# 🔧 CORREÇÃO FINAL DO SISTEMA

echo "🔧 CORREÇÃO FINAL - SISTEMA RURAL"
echo "================================="

# 1. Parar todos os processos Gunicorn
echo "⏹️ Parando processos Gunicorn..."
pkill -f gunicorn
sleep 2

# 2. Remover socket antigo
echo "🗑️ Removendo socket antigo..."
rm -f /home/django/sistema-rural/sistema_rural.sock

# 3. Corrigir permissões
echo "🔐 Corrigindo permissões..."
chown -R django:django /home/django/sistema-rural
chmod 755 /home/django/sistema-rural/sistema_rural.sock 2>/dev/null || echo "Socket não existe ainda"

# 4. Reiniciar serviço systemd
echo "🔄 Reiniciando serviço systemd..."
systemctl daemon-reload
systemctl restart sistema-rural

# 5. Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 5

# 6. Verificar status
echo "📊 Verificando status..."
systemctl status sistema-rural --no-pager -l

# 7. Verificar socket
echo "🔗 Verificando socket..."
ls -la /home/django/sistema-rural/sistema_rural.sock

# 8. Verificar processos
echo "🔍 Verificando processos Gunicorn..."
ps aux | grep gunicorn | grep -v grep

# 9. Testar conectividade
echo "🌐 Testando conectividade..."
curl -I http://localhost 2>/dev/null || echo "Erro na conectividade"

# 10. Se ainda não funcionar, iniciar manualmente
if ! systemctl is-active --quiet sistema-rural; then
    echo "🚀 Iniciando Gunicorn manualmente..."
    sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && nohup gunicorn --workers 3 --bind unix:/home/django/sistema-rural/sistema_rural.sock sistema_rural.wsgi:application > /home/django/sistema-rural/gunicorn.log 2>&1 &"
    sleep 3
    echo "🔗 Verificando socket após start manual..."
    ls -la /home/django/sistema-rural/sistema_rural.sock
fi

echo ""
echo "🎯 CORREÇÃO FINAL CONCLUÍDA!"
echo "============================"
echo "Acesse: http://45.32.219.76"



