#!/bin/bash

echo "🔍 DIAGNÓSTICO DETALHADO DO SISTEMA"
echo "=================================="

# Verificar se o Django está realmente rodando
echo "1️⃣ Processos Python rodando:"
ps aux | grep python | grep -v grep

# Verificar porta 8000 especificamente
echo ""
echo "2️⃣ Porta 8000:"
netstat -tlnp | grep :8000

# Verificar se há algum processo escutando na porta 8000
echo ""
echo "3️⃣ Processos escutando na porta 8000:"
lsof -i :8000 2>/dev/null || echo "lsof não disponível"

# Verificar logs do Django
echo ""
echo "4️⃣ Logs do Django:"
if [ -f /tmp/django.log ]; then
    echo "Últimas 20 linhas do log:"
    tail -20 /tmp/django.log
else
    echo "Arquivo de log não encontrado"
fi

# Verificar se há erros
echo ""
echo "5️⃣ Verificando erros:"
grep -i error /tmp/django.log 2>/dev/null | tail -10 || echo "Nenhum erro encontrado"

# Testar Django localmente
echo ""
echo "6️⃣ Testando Django localmente:"
curl -I http://localhost:8000 2>/dev/null || echo "Erro na conexão local"

# Verificar configuração
echo ""
echo "7️⃣ Testando configuração Django:"
cd /home/django/sistema-rural
source venv/bin/activate
python manage.py check --settings=sistema_rural.settings_producao

# Verificar firewall
echo ""
echo "8️⃣ Firewall:"
ufw status

# Verificar se o IP está correto
echo ""
echo "9️⃣ IP do servidor:"
hostname -I

# Verificar se o Django consegue iniciar
echo ""
echo "🔟 Testando inicialização do Django:"
timeout 5 python manage.py runserver 127.0.0.1:8001 --settings=sistema_rural.settings_producao &
TEST_PID=$!
sleep 3
kill $TEST_PID 2>/dev/null
echo "Teste de inicialização concluído"

echo ""
echo "✅ DIAGNÓSTICO CONCLUÍDO!"


