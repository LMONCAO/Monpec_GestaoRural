#!/bin/bash
# 🔍 DIAGNÓSTICO E CORREÇÃO DO ERRO 502

echo "🔍 DIAGNÓSTICO DO ERRO 502 - SISTEMA RURAL"
echo "=========================================="

# 1. Verificar status dos serviços
echo "📊 Verificando status dos serviços..."
systemctl status sistema-rural --no-pager -l
echo ""
systemctl status nginx --no-pager -l
echo ""

# 2. Verificar se o arquivo socket existe
echo "🔗 Verificando arquivo socket..."
ls -la /home/django/sistema-rural/sistema_rural.sock
echo ""

# 3. Verificar permissões
echo "🔐 Verificando permissões..."
ls -la /home/django/sistema-rural/
echo ""

# 4. Verificar logs de erro
echo "📋 Logs do sistema-rural:"
journalctl -u sistema-rural --no-pager -n 20
echo ""

echo "📋 Logs do nginx:"
journalctl -u nginx --no-pager -n 10
echo ""

# 5. Verificar se o Django está configurado corretamente
echo "🐍 Verificando configuração Django..."
cd /home/django/sistema-rural
sudo -u django bash -c "source venv/bin/activate && python manage.py check --settings=sistema_rural.settings_producao"
echo ""

# 6. Tentar iniciar manualmente o Gunicorn
echo "🚀 Tentando iniciar Gunicorn manualmente..."
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && gunicorn --workers 3 --bind unix:/home/django/sistema-rural/sistema_rural.sock sistema_rural.wsgi:application --daemon"
echo ""

# 7. Verificar se o socket foi criado
echo "🔗 Verificando socket após restart..."
sleep 2
ls -la /home/django/sistema-rural/sistema_rural.sock
echo ""

# 8. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
systemctl restart sistema-rural
systemctl restart nginx
echo ""

# 9. Verificar status final
echo "✅ Status final dos serviços:"
systemctl status sistema-rural --no-pager -l
echo ""

# 10. Testar conectividade
echo "🌐 Testando conectividade..."
curl -I http://localhost 2>/dev/null || echo "Erro na conectividade local"
echo ""

echo "🎯 DIAGNÓSTICO CONCLUÍDO!"
echo "========================="
echo "Se ainda houver problemas, verifique:"
echo "• Logs: journalctl -u sistema-rural -f"
echo "• Socket: ls -la /home/django/sistema-rural/sistema_rural.sock"
echo "• Permissões: chown -R django:django /home/django/sistema-rural"



