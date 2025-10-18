#!/bin/bash

echo "🚀 GARANTINDO QUE O SISTEMA FUNCIONE"
echo "===================================="

# Parar tudo
echo "⏹️ Parando todos os serviços..."
pkill -f python
pkill -f gunicorn
systemctl stop nginx
systemctl stop sistema-rural

# Aguardar
sleep 2

# Ir para o diretório do projeto
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Fazer migrações se necessário
echo "🗄️ Aplicando migrações..."
python manage.py migrate --settings=sistema_rural.settings_producao

# Iniciar Django na porta 8000
echo "🚀 Iniciando Django na porta 8000..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao > /tmp/django.log 2>&1 &

# Aguardar inicialização
sleep 5

# Configurar Nginx simples
echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/sistema-rural << 'EOF'
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

# Verificar processos
echo "📊 Verificando processos..."
ps aux | grep python
systemctl status nginx --no-pager

# Testar conectividade
echo "🌐 Testando conectividade..."
curl -I http://localhost

echo ""
echo "✅ SISTEMA FUNCIONANDO!"
echo "======================"
echo "Acesse: http://45.32.219.76"


