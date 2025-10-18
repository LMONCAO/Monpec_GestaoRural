#!/bin/bash

echo "🚀 SISTEMA SIMPLES DEFINITIVO"
echo "============================="

# Parar tudo
pkill -f python
systemctl stop nginx
sleep 2

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

# Configurar firewall para várias portas
echo "🔥 Configurando firewall..."
ufw allow 8000
ufw allow 8080
ufw allow 9000
ufw allow 3000

# Iniciar Django na porta 9000
echo "🚀 Iniciando Django na porta 9000..."
nohup python manage.py runserver 0.0.0.0:9000 --settings=sistema_rural.settings_producao > /tmp/django_9000.log 2>&1 &

# Aguardar
sleep 5

# Verificar se está rodando
echo "📊 Verificando processo..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta 9000
echo "🔍 Verificando porta 9000..."
netstat -tlnp | grep :9000

# Testar localmente
echo "🌐 Testando localmente na porta 9000..."
curl -I http://localhost:9000

# Verificar logs
echo "📋 Logs do Django na porta 9000:"
tail -5 /tmp/django_9000.log

echo ""
echo "✅ SISTEMA SIMPLES DEFINITIVO CONCLUÍDO!"
echo "========================================"
echo "Tente acessar: http://45.32.219.76:9000"


