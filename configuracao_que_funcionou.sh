#!/bin/bash

echo "🔧 APLICANDO CONFIGURAÇÃO QUE FUNCIONOU"
echo "======================================="

# Parar tudo
pkill -f python
systemctl stop nginx
sleep 2

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar configuração
echo "🔍 Verificando configuração Django..."
python manage.py check --settings=sistema_rural.settings_producao

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Configurar Nginx para redirecionar para o Django
echo "🌐 Configurando Nginx..."
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
}
EOF

# Ativar configuração
echo "🔗 Ativando configuração Nginx..."
ln -sf /etc/nginx/sites-available/sistema-rural /etc/nginx/sites-enabled
rm -f /etc/nginx/sites-enabled/default

# Testar configuração
echo "🔍 Testando configuração Nginx..."
nginx -t

# Recarregar Nginx
echo "🔄 Recarregando Nginx..."
systemctl reload nginx

# Iniciar Django na porta 8000
echo "🚀 Iniciando Django na porta 8000..."
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &"

# Aguardar
sleep 5

# Verificar status
echo "📊 Verificando status..."
ps aux | grep "python.*manage.py" | grep -v grep
systemctl status nginx --no-pager

# Testar conectividade
echo "🌐 Testando conectividade..."
curl -I http://localhost

echo ""
echo "✅ CONFIGURAÇÃO QUE FUNCIONOU APLICADA!"
echo "======================================="
echo "Acesse: http://45.32.219.76"


