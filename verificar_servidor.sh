#!/bin/bash

echo "🔍 VERIFICANDO STATUS DO SERVIDOR"
echo "=================================="

# Verificar se o servidor está funcionando
echo "1️⃣ Uptime do servidor:"
uptime

# Verificar uso de CPU e memória
echo ""
echo "2️⃣ Uso de recursos:"
free -h
echo ""
df -h

# Verificar se o Django está rodando
echo ""
echo "3️⃣ Processos Django:"
ps aux | grep python | grep manage.py

# Verificar portas abertas
echo ""
echo "4️⃣ Portas abertas:"
netstat -tlnp | grep :8000
netstat -tlnp | grep :8080

# Verificar firewall
echo ""
echo "5️⃣ Status do firewall:"
ufw status

# Verificar logs do Django
echo ""
echo "6️⃣ Logs do Django (últimas 10 linhas):"
if [ -f /tmp/django.log ]; then
    tail -10 /tmp/django.log
else
    echo "Log não encontrado"
fi

# Testar conectividade local
echo ""
echo "7️⃣ Testando conectividade local:"
curl -I http://localhost:8000 2>/dev/null || echo "Erro na conexão local"

# Verificar IP do servidor
echo ""
echo "8️⃣ IP do servidor:"
hostname -I

echo ""
echo "✅ VERIFICAÇÃO CONCLUÍDA!"


