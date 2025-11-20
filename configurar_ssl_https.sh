#!/bin/bash
# Script para configurar SSL/HTTPS com Let's Encrypt
# Sistema Monpec - Servidor Locaweb

echo "🔒 ====================================="
echo "   CONFIGURAÇÃO SSL/HTTPS"
echo "   Sistema Monpec"
echo "======================================="
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Execute como root: sudo $0"
    exit 1
fi

# Variáveis
DOMAIN="monpec.com.br"
EMAIL="admin@monpec.com.br"
WEBROOT="/var/www/monpec.com.br"

echo "📋 Configurações:"
echo "   Domínio: $DOMAIN"
echo "   Email: $EMAIL"
echo "   Webroot: $WEBROOT"
echo ""

# 1. Instalar Certbot
echo "📦 1/5 - Instalando Certbot..."
yum install -y certbot python3-certbot-nginx

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar Certbot"
    exit 1
fi

echo "✅ Certbot instalado"
echo ""

# 2. Obter certificado SSL
echo "🔐 2/5 - Obtendo certificado SSL Let's Encrypt..."
echo "   Este processo pode solicitar confirmação"
echo ""

certbot --nginx \
    -d $DOMAIN \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    --redirect

if [ $? -ne 0 ]; then
    echo "⚠️ Erro ao obter certificado. Tentando método alternativo..."
    
    # Método alternativo: webroot
    certbot certonly \
        --webroot \
        -w $WEBROOT/static \
        -d $DOMAIN \
        --non-interactive \
        --agree-tos \
        --email $EMAIL
    
    if [ $? -ne 0 ]; then
        echo "❌ Não foi possível obter certificado SSL"
        echo "   Verifique se:"
        echo "   1. O domínio $DOMAIN aponta para este servidor"
        echo "   2. A porta 80 está acessível externamente"
        echo "   3. Nginx está rodando"
        exit 1
    fi
fi

echo "✅ Certificado SSL obtido com sucesso"
echo ""

# 3. Configurar Nginx para HTTPS
echo "🌐 3/5 - Configurando Nginx para HTTPS..."

cat > /etc/nginx/conf.d/monpec_https.conf << 'EOF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name monpec.com.br;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name monpec.com.br;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/monpec.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monpec.com.br/privkey.pem;
    
    # SSL Configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    
    # SSL Session
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    
    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    ssl_trusted_certificate /etc/letsencrypt/live/monpec.com.br/chain.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Proxy para Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /var/www/monpec.com.br/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /var/www/monpec.com.br/media/;
        expires 7d;
    }
}
EOF

echo "✅ Configuração HTTPS criada"
echo ""

# 4. Testar configuração do Nginx
echo "🧪 4/5 - Testando configuração do Nginx..."
nginx -t

if [ $? -ne 0 ]; then
    echo "❌ Erro na configuração do Nginx"
    exit 1
fi

echo "✅ Configuração do Nginx válida"
echo ""

# 5. Reiniciar Nginx
echo "🔄 5/5 - Reiniciando Nginx..."
systemctl restart nginx

if [ $? -ne 0 ]; then
    echo "❌ Erro ao reiniciar Nginx"
    exit 1
fi

echo "✅ Nginx reiniciado"
echo ""

# 6. Configurar renovação automática
echo "🔄 Configurando renovação automática..."

# Testar renovação
certbot renew --dry-run

if [ $? -eq 0 ]; then
    echo "✅ Renovação automática configurada"
    echo "   Certificados serão renovados automaticamente"
else
    echo "⚠️ Verificar renovação automática manualmente"
fi

echo ""

# 7. Verificar SSL
echo "🔐 Verificando SSL..."
echo "   Testando conexão HTTPS..."

sleep 2

if command -v curl &> /dev/null; then
    curl -I https://$DOMAIN 2>&1 | head -5
fi

echo ""
echo "✅ ====================================="
echo "   SSL/HTTPS CONFIGURADO COM SUCESSO!"
echo "======================================="
echo ""
echo "🌐 Acesse: https://$DOMAIN"
echo ""
echo "📊 Próximos passos:"
echo "   1. Teste no navegador: https://$DOMAIN"
echo "   2. Verifique certificado (cadeado verde)"
echo "   3. Teste SSL Labs: https://www.ssllabs.com/ssltest/"
echo "   4. Configure Django: SECURE_SSL_REDIRECT = True"
echo ""
echo "🔄 Renovação automática:"
echo "   O Certbot renova automaticamente via cron/systemd"
echo "   Próxima renovação em ~60 dias"
echo ""

