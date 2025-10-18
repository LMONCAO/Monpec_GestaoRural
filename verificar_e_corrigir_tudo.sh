#!/bin/bash

echo "🔍 VERIFICANDO E CORRIGINDO TUDO"
echo "================================"

# Verificar se há processos Python rodando
echo "1️⃣ Processos Python:"
ps aux | grep python | grep -v grep

# Verificar portas abertas
echo ""
echo "2️⃣ Portas abertas:"
netstat -tlnp | grep :8000
netstat -tlnp | grep :80

# Verificar logs do Django
echo ""
echo "3️⃣ Logs do Django:"
if [ -f /tmp/django.log ]; then
    tail -10 /tmp/django.log
else
    echo "Log não encontrado"
fi

# Parar tudo
echo ""
echo "4️⃣ Parando tudo..."
pkill -f python
systemctl stop nginx
sleep 3

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar configuração
echo ""
echo "5️⃣ Verificando configuração Django:"
python manage.py check --settings=sistema_rural.settings_producao

# Coletar arquivos estáticos
echo ""
echo "6️⃣ Coletando arquivos estáticos:"
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Configurar firewall
echo ""
echo "7️⃣ Configurando firewall:"
ufw allow 8000
ufw allow 8080

# Iniciar Django na porta 8000
echo ""
echo "8️⃣ Iniciando Django na porta 8000:"
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar
sleep 8

# Verificar se está rodando
echo ""
echo "9️⃣ Verificando Django:"
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta 8000
echo ""
echo "🔟 Verificando porta 8000:"
netstat -tlnp | grep :8000

# Testar localmente
echo ""
echo "🌐 Testando localmente:"
curl -I http://localhost:8000

# Verificar logs
echo ""
echo "📋 Últimas linhas do log:"
tail -5 /tmp/django.log

echo ""
echo "✅ VERIFICAÇÃO E CORREÇÃO CONCLUÍDA!"
echo "===================================="
echo "Tente acessar: http://45.32.219.76:8000"


