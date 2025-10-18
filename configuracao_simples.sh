#!/bin/bash

echo "🔧 CONFIGURAÇÃO SIMPLES DO SISTEMA"
echo "=================================="

# Parar tudo
pkill -f python
systemctl stop nginx
sleep 2

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se o banco de dados está OK
echo "🗄️ Verificando banco de dados..."
python manage.py migrate --settings=sistema_rural.settings_producao

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Permitir todas as portas no firewall
echo "🔓 Configurando firewall..."
ufw allow 8000
ufw allow 8080
ufw allow 80

# Iniciar Django na porta 8000
echo "🚀 Iniciando Django na porta 8000..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar
sleep 8

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
echo "📋 Logs do Django:"
tail -10 /tmp/django.log

echo ""
echo "✅ CONFIGURAÇÃO SIMPLES CONCLUÍDA!"
echo "=================================="
echo "Tente acessar: http://45.32.219.76:8000"


