#!/bin/bash

echo "🔍 DIAGNÓSTICO COMPLETO FINAL"
echo "============================="

# Verificar se o Django está realmente rodando
echo "1️⃣ Processos Python:"
ps aux | grep python | grep -v grep

# Verificar portas
echo ""
echo "2️⃣ Portas abertas:"
netstat -tlnp | grep :8000
netstat -tlnp | grep :80

# Verificar logs
echo ""
echo "3️⃣ Logs do Django:"
if [ -f /tmp/django.log ]; then
    tail -20 /tmp/django.log
else
    echo "Log não encontrado"
fi

# Verificar se há erros
echo ""
echo "4️⃣ Verificando erros:"
grep -i error /tmp/django.log 2>/dev/null | tail -10 || echo "Nenhum erro encontrado"

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

# Verificar IP do servidor
echo ""
echo "7️⃣ IP do servidor:"
hostname -I

# Testar Django localmente
echo ""
echo "8️⃣ Testando Django localmente:"
curl -I http://localhost:8000 2>/dev/null || echo "Erro na conexão local"

# Verificar se o Django consegue iniciar
echo ""
echo "9️⃣ Testando inicialização do Django:"
timeout 5 python manage.py runserver 127.0.0.1:8001 --settings=sistema_rural.settings_producao &
TEST_PID=$!
sleep 3
kill $TEST_PID 2>/dev/null
echo "Teste de inicialização concluído"

# Verificar espaço em disco
echo ""
echo "🔟 Espaço em disco:"
df -h

echo ""
echo "✅ DIAGNÓSTICO COMPLETO FINAL CONCLUÍDO!"


