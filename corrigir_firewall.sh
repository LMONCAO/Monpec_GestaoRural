#!/bin/bash

echo "🔥 CORRIGINDO FIREWALL"
echo "====================="

# Verificar status do firewall
echo "📊 Status do firewall:"
ufw status

# Permitir porta 8000
echo "🔓 Permitindo porta 8000..."
ufw allow 8000

# Permitir porta 80
echo "🔓 Permitindo porta 80..."
ufw allow 80

# Permitir SSH
echo "🔓 Permitindo SSH..."
ufw allow ssh

# Verificar se o Django está rodando
echo "📊 Verificando processo Django..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta
echo "🔍 Verificando porta 8000..."
netstat -tlnp | grep :8000

# Testar conectividade externa
echo "🌐 Testando conectividade..."
curl -I http://localhost:8000

echo ""
echo "✅ FIREWALL CORRIGIDO!"
echo "====================="
echo "Acesse: http://45.32.219.76:8000"


