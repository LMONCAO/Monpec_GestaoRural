#!/bin/bash

echo "🔄 REINICIANDO SERVIDOR COMPLETO"
echo "================================"

# Parar tudo
echo "⏹️ Parando todos os serviços..."
pkill -f python
systemctl stop nginx
systemctl stop sistema-rural

# Aguardar
sleep 3

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

# Configurar firewall
echo "🔥 Configurando firewall..."
ufw allow 8000
ufw allow 8080
ufw allow 9000

# Iniciar Django na porta 8080
echo "🚀 Iniciando Django na porta 8080..."
nohup python manage.py runserver 0.0.0.0:8080 --settings=sistema_rural.settings_producao > /tmp/django_8080.log 2>&1 &

# Aguardar
sleep 5

# Verificar se está rodando
echo "📊 Verificando processo..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta 8080
echo "🔍 Verificando porta 8080..."
netstat -tlnp | grep :8080

# Testar localmente
echo "🌐 Testando localmente..."
curl -I http://localhost:8080

# Verificar logs
echo "📋 Logs do Django:"
tail -5 /tmp/django_8080.log

echo ""
echo "✅ SERVIDOR REINICIADO!"
echo "======================"
echo "Tente acessar: http://45.32.219.76:8080"


