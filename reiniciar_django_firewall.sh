#!/bin/bash

echo "🚀 REINICIANDO DJANGO COM FIREWALL CONFIGURADO"
echo "=============================================="

# Parar Django existente
echo "⏹️ Parando Django existente..."
pkill -f "python.*manage.py"
sleep 2

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar configuração
echo "🔍 Verificando configuração Django..."
python manage.py check --settings=sistema_rural.settings_producao

# Iniciar Django
echo "🚀 Iniciando Django..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar inicialização
sleep 5

# Verificar se está rodando
echo "📊 Verificando processo Django..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta
echo "🔍 Verificando porta 8000..."
netstat -tlnp | grep :8000

# Testar localmente
echo "🌐 Testando conectividade local..."
curl -I http://localhost:8000

# Verificar logs
echo "📋 Logs do Django:"
tail -5 /tmp/django.log

echo ""
echo "✅ DJANGO REINICIADO COM FIREWALL!"
echo "=================================="
echo "Acesse: http://45.32.219.76:8000"


