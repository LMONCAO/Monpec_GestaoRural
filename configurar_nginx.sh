#!/bin/bash

echo "🔧 CONFIGURANDO NGINX PARA PORTA 8000"
echo "====================================="

# Parar Nginx
systemctl stop nginx

# Criar configuração simples
cat > /etc/nginx/sites-available/sistema-rural << 'EOF'
server {
    listen 80;
    server_name 45.32.219.76;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/django/sistema-rural/staticfiles/;
    }
}
EOF

# Testar configuração
echo "🔍 Testando configuração Nginx..."
nginx -t

# Iniciar Nginx
echo "🌐 Iniciando Nginx..."
systemctl start nginx

# Verificar status
echo "📊 Status do Nginx:"
systemctl status nginx --no-pager

echo ""
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================="
echo "Acesse: http://45.32.219.76"


