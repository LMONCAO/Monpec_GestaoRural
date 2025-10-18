#!/bin/bash

echo "🔄 REINICIANDO SISTEMA COMPLETO"
echo "==============================="

# Parar tudo
echo "⏹️ Parando todos os processos..."
pkill -f python
pkill -f gunicorn
systemctl stop nginx
systemctl stop sistema-rural

# Aguardar
sleep 3

# Verificar firewall
echo "🔥 Verificando firewall..."
ufw status

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar configuração
echo "🔍 Verificando configuração..."
python manage.py check --settings=sistema_rural.settings_producao

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Iniciar Django
echo "🚀 Iniciando Django..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar
sleep 5

# Verificar se está rodando
echo "📊 Verificando processo..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta
echo "🔍 Verificando porta 8000..."
netstat -tlnp | grep :8000

# Testar localmente
echo "🌐 Testando localmente..."
curl -I http://localhost:8000

# Verificar logs
echo "📋 Últimas linhas do log:"
tail -5 /tmp/django.log

echo ""
echo "✅ SISTEMA REINICIADO!"
echo "====================="
echo "Acesse: http://45.32.219.76:8000"


