#!/bin/bash
# 🔧 CORREÇÃO DA CONFIGURAÇÃO NGINX

echo "🔧 CORRIGINDO CONFIGURAÇÃO NGINX"
echo "================================="

# 1. Verificar configuração atual
echo "🔍 Verificando configuração atual do Nginx..."
nginx -t
echo ""

# 2. Verificar arquivo de configuração
echo "📋 Conteúdo do arquivo de configuração:"
cat /etc/nginx/sites-available/sistema-rural
echo ""

# 3. Verificar se o arquivo proxy_params existe
echo "🔗 Verificando arquivo proxy_params..."
if [ -f /etc/nginx/proxy_params ]; then
    echo "✅ Arquivo proxy_params existe:"
    cat /etc/nginx/proxy_params
else
    echo "❌ Arquivo proxy_params não existe, criando..."
    cat > /etc/nginx/proxy_params << 'EOF'
proxy_set_header Host $http_host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_redirect off;
proxy_buffering off;
EOF
fi
echo ""

# 4. Corrigir configuração do Nginx
echo "🔧 Corrigindo configuração do Nginx..."
cat > /etc/nginx/sites-available/sistema-rural << 'EOF'
server {
    listen 80;
    server_name 45.32.219.76;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        root /home/django/sistema-rural;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://unix:/home/django/sistema-rural/sistema_rural.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;
    }
}
EOF

# 5. Testar configuração
echo "🧪 Testando configuração do Nginx..."
nginx -t
echo ""

# 6. Reiniciar Nginx
echo "🔄 Reiniciando Nginx..."
systemctl restart nginx

# 7. Verificar status
echo "📊 Verificando status do Nginx..."
systemctl status nginx --no-pager -l
echo ""

# 8. Verificar se o socket está acessível
echo "🔗 Verificando acesso ao socket..."
ls -la /home/django/sistema-rural/sistema_rural.sock
echo ""

# 9. Testar conectividade
echo "🌐 Testando conectividade..."
curl -I http://localhost 2>/dev/null || echo "Erro na conectividade local"
echo ""

# 10. Verificar logs do Nginx
echo "📋 Logs do Nginx (últimas 10 linhas):"
journalctl -u nginx --no-pager -n 10
echo ""

echo "🎯 CORREÇÃO DO NGINX CONCLUÍDA!"
echo "==============================="
echo "Acesse: http://45.32.219.76"



