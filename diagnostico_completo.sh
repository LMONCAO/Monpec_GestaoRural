#!/bin/bash

echo "🔍 DIAGNÓSTICO COMPLETO DO SISTEMA"
echo "=================================="

# Verificar se o Django está rodando
echo "1️⃣ Verificando processo Django:"
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta 8000
echo ""
echo "2️⃣ Verificando porta 8000:"
netstat -tlnp | grep :8000

# Verificar logs do Django
echo ""
echo "3️⃣ Logs do Django (últimas 10 linhas):"
tail -10 /tmp/django.log

# Verificar se há erros
echo ""
echo "4️⃣ Verificando erros nos logs:"
grep -i error /tmp/django.log | tail -5

# Verificar configuração Django
echo ""
echo "5️⃣ Testando configuração Django:"
cd /home/django/sistema-rural
source venv/bin/activate
python manage.py check --settings=sistema_rural.settings_producao

# Verificar firewall
echo ""
echo "6️⃣ Status do firewall:"
ufw status

# Verificar se o serviço está ativo
echo ""
echo "7️⃣ Verificando serviços:"
systemctl status nginx --no-pager
echo ""
systemctl status sistema-rural --no-pager

# Testar conectividade local
echo ""
echo "8️⃣ Testando conectividade local:"
curl -I http://localhost:8000 2>/dev/null || echo "Erro na conexão local"

# Verificar processos Python
echo ""
echo "9️⃣ Todos os processos Python:"
ps aux | grep python | grep -v grep

# Verificar espaço em disco
echo ""
echo "🔟 Espaço em disco:"
df -h

echo ""
echo "✅ DIAGNÓSTICO CONCLUÍDO!"


