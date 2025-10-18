#!/bin/bash

echo "🌐 CONFIGURANDO REDE VULTR"
echo "=========================="

# Verificar interfaces de rede
echo "1️⃣ Interfaces de rede:"
ip addr show

# Verificar roteamento
echo ""
echo "2️⃣ Tabela de roteamento:"
ip route show

# Verificar firewall
echo ""
echo "3️⃣ Status do firewall:"
ufw status verbose

# Permitir ICMP explicitamente
echo ""
echo "4️⃣ Permitindo ICMP (ping)..."
ufw allow in on any to any port 22
ufw allow in on any to any port 80
ufw allow in on any to any port 443
ufw allow in on any to any port 8000
ufw allow in on any to any port 8080

# Configurar iptables para permitir ICMP
echo ""
echo "5️⃣ Configurando iptables para ICMP..."
iptables -I INPUT -p icmp --icmp-type echo-request -j ACCEPT
iptables -I OUTPUT -p icmp --icmp-type echo-reply -j ACCEPT

# Verificar se Django está rodando
echo ""
echo "6️⃣ Verificando Django..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta 8000
echo ""
echo "7️⃣ Verificando porta 8000..."
netstat -tlnp | grep :8000

# Testar conectividade local
echo ""
echo "8️⃣ Testando conectividade local..."
curl -I http://localhost:8000

# Verificar IP público
echo ""
echo "9️⃣ IP público do servidor:"
curl -s ifconfig.me

echo ""
echo "✅ CONFIGURAÇÃO DE REDE CONCLUÍDA!"
echo "=================================="
echo "Tente acessar: http://45.32.219.76:8000"


