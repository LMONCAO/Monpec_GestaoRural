#!/bin/bash

echo "🚀 INICIANDO DJANGO DIRETO NA PORTA 80"
echo "======================================"

# Parar tudo
pkill -f python
systemctl stop nginx
sleep 3

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar configuração
python manage.py check --settings=sistema_rural.settings_producao

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Permitir porta 80 no firewall
ufw allow 80

# Iniciar Django diretamente na porta 80
echo "🚀 Iniciando Django na porta 80..."
nohup python manage.py runserver 0.0.0.0:80 --settings=sistema_rural.settings_producao > /tmp/django_80.log 2>&1 &

# Aguardar
sleep 8

# Verificar se está rodando
echo "📊 Verificando Django na porta 80..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta 80
echo "🔍 Verificando porta 80..."
netstat -tlnp | grep :80

# Testar localmente
echo "🌐 Testando localmente..."
curl -I http://localhost:80

echo ""
echo "✅ DJANGO DIRETO NA PORTA 80!"
echo "============================="
echo "Acesse: http://45.32.219.76"


