#!/bin/bash
# 🔧 CORRIGINDO E EXECUTANDO DEPLOY COMPLETO

echo "🚀 CORRIGINDO E EXECUTANDO DEPLOY COMPLETO"
echo "=========================================="

# 1. Criar usuário django se não existir
echo "👤 Criando usuário django..."
useradd -m -s /bin/bash django 2>/dev/null || echo "Usuário django já existe"

# 2. Criar diretório do projeto
echo "📁 Criando diretório do projeto..."
mkdir -p /home/django/sistema-rural
chown -R django:django /home/django

# 3. Extrair arquivos
echo "📦 Extraindo arquivos..."
cd /tmp
tar -xzf sistema-rural-deploy.tar.gz -C /home/django/sistema-rural/
chown -R django:django /home/django/sistema-rural

# 4. Instalar dependências do sistema
echo "📦 Instalando dependências do sistema..."
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# 5. Configurar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE sistema_rural;" 2>/dev/null || echo "Banco já existe"
sudo -u postgres psql -c "CREATE USER django_user WITH PASSWORD 'Django2025@';" 2>/dev/null || echo "Usuário já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sistema_rural TO django_user;"

# 6. Configurar ambiente Python
echo "🐍 Configurando ambiente Python..."
cd /home/django/sistema-rural
sudo -u django python3 -m venv venv
sudo -u django bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u django bash -c "source venv/bin/activate && pip install Django==4.2.7 gunicorn==21.2.0 psycopg2-binary==2.9.9 whitenoise==6.6.0 python-decouple==3.8 pillow==10.1.0"

# 7. Criar arquivo .env
echo "🔐 Criando arquivo .env..."
sudo -u django bash -c "cat > /home/django/sistema-rural/.env << 'EOF'
DEBUG=False
SECRET_KEY=django-insecure-sistema-rural-ia-2025-producao-segura
DB_NAME=sistema_rural
DB_USER=django_user
DB_PASSWORD=Django2025@
DB_HOST=localhost
DB_PORT=5432
EOF"

# 8. Criar settings_producao.py
echo "⚙️ Criando configuração de produção..."
sudo -u django bash -c "cat > /home/django/sistema-rural/sistema_rural/settings_producao.py << 'EOF'
import os
from decouple import config
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['45.32.219.76', 'localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='sistema_rural'),
        'USER': config('DB_USER', default='django_user'),
        'PASSWORD': config('DB_PASSWORD', default='Django2025@'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SECRET_KEY = config('SECRET_KEY', default='django-insecure-sistema-rural-ia-2025-producao-segura')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/django/sistema-rural/sistema_rural.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
EOF"

# 9. Configurar Django
echo "🔧 Configurando Django..."
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao"
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && python manage.py migrate --settings=sistema_rural.settings_producao"

# 10. Criar superusuário
echo "👤 Criando superusuário..."
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && echo 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username=\"admin\").exists() or User.objects.create_superuser(\"admin\", \"admin@sistema-rural.com\", \"admin123\")' | python manage.py shell --settings=sistema_rural.settings_producao"

# 11. Configurar Gunicorn
echo "🚀 Configurando Gunicorn..."
cat > /etc/systemd/system/sistema-rural.service << 'EOF'
[Unit]
Description=Gunicorn daemon for Sistema Rural
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/sistema-rural
ExecStart=/home/django/sistema-rural/venv/bin/gunicorn --workers 3 --bind unix:/home/django/sistema-rural/sistema_rural.sock sistema_rural.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 12. Configurar Nginx
echo "🌐 Configurando Nginx..."
cat > /etc/nginx/sites-available/sistema-rural << 'EOF'
server {
    listen 80;
    server_name 45.32.219.76;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/django/sistema-rural;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/sistema-rural/sistema_rural.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 13. Ativar serviços
echo "⚙️ Ativando serviços..."
ln -sf /etc/nginx/sites-available/sistema-rural /etc/nginx/sites-enabled
rm -f /etc/nginx/sites-enabled/default
systemctl daemon-reload
nginx -t
systemctl start sistema-rural
systemctl enable sistema-rural
systemctl restart nginx

# 14. Configurar firewall
echo "🔥 Configurando firewall..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# 15. Verificar status
echo "🔍 Verificando status..."
systemctl status sistema-rural --no-pager -l
systemctl status nginx --no-pager -l

echo ""
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "================================"
echo "🌐 Sistema: http://45.32.219.76"
echo "👤 Admin: http://45.32.219.76/admin"
echo "🔑 Login: admin / admin123"
echo ""
echo "📋 Comandos úteis:"
echo "• Ver logs: journalctl -u sistema-rural -f"
echo "• Reiniciar: systemctl restart sistema-rural"
echo "• Status: systemctl status sistema-rural"



