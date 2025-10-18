#!/bin/bash

echo "🌐 CONFIGURANDO NGINX FINAL"
echo "============================"

# Parar Nginx
systemctl stop nginx

# Configurar Nginx para redirecionar para porta 8000
cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias /home/django/sistema-rural/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Testar configuração
echo "🔍 Testando configuração Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuração válida!"
    
    # Iniciar Nginx
    echo "🚀 Iniciando Nginx..."
    systemctl start nginx
    
    # Verificar status
    echo "📊 Status do Nginx:"
    systemctl status nginx --no-pager
    
    echo ""
    echo "✅ NGINX CONFIGURADO!"
    echo "===================="
    echo "Acesse: http://45.32.219.76 (sem porta)"
    echo "Ou: http://45.32.219.76:8000 (direto)"
else
    echo "❌ Erro na configuração do Nginx"
fi


