#!/bin/bash

echo "🚀 INICIANDO SISTEMA RURAL COMPLETO"
echo "==================================="

# Parar processos existentes
echo "⏹️ Parando processos existentes..."
pkill -f "python.*manage.py"
pkill -f gunicorn
systemctl stop nginx 2>/dev/null

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

# Iniciar Django em background
echo "🚀 Iniciando Django..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 8

# Verificar se está rodando
echo "📊 Verificando processo Django..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta
echo "🔍 Verificando porta 8000..."
netstat -tlnp | grep :8000

# Testar localmente
echo "🌐 Testando conectividade local..."
curl -I http://localhost:8000

echo ""
echo "✅ SISTEMA INICIADO!"
echo "==================="
echo "Acesse: http://45.32.219.76:8000"
echo "Logs: tail -f /tmp/django.log"


