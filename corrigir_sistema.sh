#!/bin/bash

echo "🔧 CORRIGINDO SISTEMA RURAL - ERRO 502"
echo "======================================"

# Parar todos os processos
echo "⏹️ Parando processos..."
pkill -f gunicorn
systemctl stop sistema-rural
systemctl stop nginx

# Aguardar
sleep 2

# Remover socket antigo
echo "🗑️ Removendo socket antigo..."
rm -f /home/django/sistema-rural/sistema_rural.sock

# Verificar permissões
echo "🔐 Corrigindo permissões..."
chown -R django:www-data /home/django/sistema-rural/
chmod -R 755 /home/django/sistema-rural/

# Verificar se o arquivo wsgi.py está correto
echo "🔍 Verificando configuração Django..."
cd /home/django/sistema-rural
sudo -u django bash -c 'source venv/bin/activate && python manage.py check --settings=sistema_rural.settings_producao'

# Iniciar Gunicorn manualmente primeiro
echo "🚀 Iniciando Gunicorn manualmente..."
sudo -u django bash -c 'cd /home/django/sistema-rural && source venv/bin/activate && nohup gunicorn --workers 3 --bind unix:/home/django/sistema-rural/sistema_rural.sock sistema_rural.wsgi:application > /tmp/gunicorn.log 2>&1 &'

# Aguardar
sleep 5

# Verificar se o socket foi criado
echo "🔗 Verificando socket..."
ls -la /home/django/sistema-rural/sistema_rural.sock

# Iniciar Nginx
echo "🌐 Iniciando Nginx..."
systemctl start nginx

# Verificar status
echo "📊 Verificando status..."
ps aux | grep gunicorn
systemctl status nginx --no-pager

# Testar
echo "🌐 Testando conectividade..."
curl -I http://localhost

echo ""
echo "✅ CORREÇÃO CONCLUÍDA!"
echo "======================"
echo "Acesse: http://45.32.219.76"


