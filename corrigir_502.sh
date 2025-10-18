#!/bin/bash
# 🔧 CORREÇÃO RÁPIDA DO ERRO 502

echo "🔧 CORRIGINDO ERRO 502 - SISTEMA RURAL"
echo "======================================"

# 1. Criar diretório static
echo "📁 Criando diretório static..."
cd /home/django/sistema-rural
mkdir -p static
chown -R django:django static

# 2. Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
sudo -u django bash -c "source venv/bin/activate && python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao"

# 3. Verificar configuração Django
echo "🔍 Verificando configuração Django..."
sudo -u django bash -c "source venv/bin/activate && python manage.py check --settings=sistema_rural.settings_producao"

# 4. Parar serviços
echo "⏹️ Parando serviços..."
systemctl stop sistema-rural
systemctl stop nginx

# 5. Remover socket antigo se existir
echo "🗑️ Removendo socket antigo..."
rm -f /home/django/sistema-rural/sistema_rural.sock

# 6. Iniciar Gunicorn manualmente
echo "🚀 Iniciando Gunicorn..."
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && gunicorn --workers 3 --bind unix:/home/django/sistema-rural/sistema_rural.sock sistema_rural.wsgi:application --daemon"

# 7. Aguardar socket ser criado
echo "⏳ Aguardando socket ser criado..."
sleep 3

# 8. Verificar se socket foi criado
echo "🔗 Verificando socket..."
ls -la /home/django/sistema-rural/sistema_rural.sock

# 9. Iniciar Nginx
echo "🌐 Iniciando Nginx..."
systemctl start nginx

# 10. Verificar status
echo "📊 Verificando status dos serviços..."
systemctl status sistema-rural --no-pager -l
echo ""
systemctl status nginx --no-pager -l

# 11. Testar conectividade
echo "🌐 Testando conectividade..."
curl -I http://localhost 2>/dev/null && echo "✅ Sistema funcionando!" || echo "❌ Ainda há problemas"

echo ""
echo "🎯 CORREÇÃO CONCLUÍDA!"
echo "====================="
echo "Acesse: http://45.32.219.76"



