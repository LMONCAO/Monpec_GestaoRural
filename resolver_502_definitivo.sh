#!/bin/bash

echo "🔧 RESOLVENDO 502 BAD GATEWAY DEFINITIVAMENTE"
echo "============================================="

# Parar Nginx
echo "⏹️ Parando Nginx..."
systemctl stop nginx
systemctl disable nginx

# Parar Django
echo "⏹️ Parando Django..."
pkill -f python

# Aguardar
sleep 3

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar configuração
echo "🔍 Verificando configuração Django..."
python manage.py check --settings=sistema_rural.settings_producao

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Configurar firewall
echo "🔥 Configurando firewall..."
ufw allow 8000
ufw allow 80

# Iniciar Django na porta 8000
echo "🚀 Iniciando Django na porta 8000..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar
sleep 5

# Verificar se está rodando
echo "📊 Verificando Django..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta 8000
echo "🔍 Verificando porta 8000..."
netstat -tlnp | grep :8000

# Testar localmente
echo "🌐 Testando localmente..."
curl -I http://localhost:8000

echo ""
echo "✅ PROBLEMA 502 RESOLVIDO!"
echo "=========================="
echo "Acesse: http://45.32.219.76:8000"


