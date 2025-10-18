#!/bin/bash

echo "🔧 CONFIGURANDO SISTEMA PERMANENTE"
echo "=================================="

# Parar tudo
pkill -f python
systemctl stop nginx
sleep 2

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar configuração
python manage.py check --settings=sistema_rural.settings_producao

# Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Configurar firewall
ufw allow 8000
ufw allow 80
ufw allow 22

# Iniciar Django na porta 8000
echo "🚀 Iniciando Django na porta 8000..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar
sleep 5

# Configurar Nginx para redirecionar para porta 8000
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
    }
    
    location /static/ {
        alias /home/django/sistema-rural/staticfiles/;
    }
}
EOF

# Testar e iniciar Nginx
nginx -t && systemctl start nginx

# Verificar status
echo "📊 Verificando status..."
ps aux | grep python | grep manage.py
netstat -tlnp | grep :8000
systemctl status nginx --no-pager

echo ""
echo "✅ SISTEMA PERMANENTE CONFIGURADO!"
echo "=================================="
echo "Acesse: http://45.32.219.76"


