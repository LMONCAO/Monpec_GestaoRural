#!/bin/bash

echo "🔧 CORRIGINDO ERRO 502 BAD GATEWAY"
echo "=================================="

# Parar tudo
echo "⏹️ Parando todos os serviços..."
pkill -f python
systemctl stop nginx
sleep 3

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar configuração
echo "🔍 Verificando configuração..."
python manage.py check --settings=sistema_rural.settings_producao

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Iniciar Django na porta 8000
echo "🚀 Iniciando Django na porta 8000..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar inicialização
echo "⏳ Aguardando Django inicializar..."
sleep 8

# Verificar se Django está rodando
echo "📊 Verificando Django..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta 8000
echo "🔍 Verificando porta 8000..."
netstat -tlnp | grep :8000

# Testar Django localmente
echo "🌐 Testando Django localmente..."
curl -I http://localhost:8000

# Configurar Nginx
echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80 default_server;
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
    }
}
EOF

# Testar configuração Nginx
echo "🔍 Testando configuração Nginx..."
nginx -t

# Iniciar Nginx
echo "🚀 Iniciando Nginx..."
systemctl start nginx

# Verificar status
echo "📊 Verificando status dos serviços..."
systemctl status nginx --no-pager

# Testar conectividade
echo "🌐 Testando conectividade..."
curl -I http://localhost

echo ""
echo "✅ CORREÇÃO 502 CONCLUÍDA!"
echo "=========================="
echo "Acesse: http://45.32.219.76"


