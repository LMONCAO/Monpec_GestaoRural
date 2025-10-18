#!/bin/bash

echo "🔥 CONFIGURANDO FIREWALL DO SERVIDOR"
echo "===================================="

# Parar o firewall temporariamente para configurar
echo "⏹️ Parando firewall temporariamente..."
ufw --force disable

# Limpar todas as regras existentes
echo "🗑️ Limpando regras existentes..."
ufw --force reset

# Configurar política padrão
echo "🔧 Configurando política padrão..."
ufw default deny incoming
ufw default allow outgoing

# Permitir SSH (porta 22)
echo "🔓 Permitindo SSH (porta 22)..."
ufw allow 22/tcp

# Permitir HTTP (porta 80)
echo "🔓 Permitindo HTTP (porta 80)..."
ufw allow 80/tcp

# Permitir HTTPS (porta 443)
echo "🔓 Permitindo HTTPS (porta 443)..."
ufw allow 443/tcp

# Permitir porta 8000 (Django)
echo "🔓 Permitindo porta 8000 (Django)..."
ufw allow 8000/tcp

# Permitir porta 8080 (alternativa)
echo "🔓 Permitindo porta 8080 (alternativa)..."
ufw allow 8080/tcp

# Permitir ICMP (ping)
echo "🔓 Permitindo ICMP (ping)..."
ufw allow in on any to any port 22
ufw allow in on any to any port 80
ufw allow in on any to any port 443
ufw allow in on any to any port 8000
ufw allow in on any to any port 8080

# Ativar firewall
echo "🚀 Ativando firewall..."
ufw --force enable

# Verificar status
echo "📊 Status do firewall:"
ufw status verbose

# Verificar se as portas estão abertas
echo ""
echo "🔍 Verificando portas abertas:"
netstat -tlnp | grep :8000
netstat -tlnp | grep :8080

echo ""
echo "✅ FIREWALL CONFIGURADO!"
echo "========================"
echo "Tente acessar: http://45.32.219.76:8000"


