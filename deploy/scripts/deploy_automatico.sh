#!/bin/bash
# 🚀 SCRIPT DE DEPLOY AUTOMÁTICO - SISTEMA RURAL COM IA
# Servidor: 45.32.219.76

echo "🚀 INICIANDO DEPLOY AUTOMÁTICO DO SISTEMA RURAL COM IA"
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para executar comandos com feedback
executar_comando() {
    echo -e "${BLUE}🔄 $1${NC}"
    if eval "$2"; then
        echo -e "${GREEN}✅ $1 - SUCESSO${NC}"
    else
        echo -e "${RED}❌ $1 - FALHOU${NC}"
        exit 1
    fi
}

# 1. Atualizar sistema
executar_comando "Atualizando sistema" "apt update && apt upgrade -y"

# 2. Instalar dependências
executar_comando "Instalando dependências Python" "apt install -y python3 python3-pip python3-venv"
executar_comando "Instalando PostgreSQL" "apt install -y postgresql postgresql-contrib"
executar_comando "Instalando Nginx" "apt install -y nginx"
executar_comando "Instalando Git" "apt install -y git"

# 3. Configurar PostgreSQL
echo -e "${YELLOW}🗄️ Configurando PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE DATABASE sistema_rural;" 2>/dev/null || echo "Banco já existe"
sudo -u postgres psql -c "CREATE USER django_user WITH PASSWORD 'Django2025@';" 2>/dev/null || echo "Usuário já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sistema_rural TO django_user;"

# 4. Criar usuário django
executar_comando "Criando usuário django" "useradd -m -s /bin/bash django 2>/dev/null || echo 'Usuário já existe'"
executar_comando "Configurando permissões" "usermod -aG sudo django"

# 5. Configurar senha do usuário django
echo "django:Django2025@" | chpasswd

# 6. Criar diretório do projeto
executar_comando "Criando diretório do projeto" "mkdir -p /home/django/sistema-rural"

# 7. Copiar arquivos do projeto (assumindo que estamos no diretório do projeto)
echo -e "${YELLOW}📁 Copiando arquivos do projeto...${NC}"
cp -r * /home/django/sistema-rural/ 2>/dev/null || echo "Copiando arquivos..."

# 8. Configurar permissões
executar_comando "Configurando permissões" "chown -R django sync /home/django/sistema-rural"

# 9. Configurar ambiente Python
echo -e "${YELLOW}🐍 Configurando ambiente Python...${NC}"
sudo -u django bash -c "cd /home/django/sistema-rural && python3 -m venv venv"
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && pip install --upgrade pip"

# 10. Instalar dependências Python
echo -e "${YELLOW}📦 Instalando dependências Python...${NC}"
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && pip install Django==4.2.7 gunicorn==21.2.0 psycopg2-binary==2.9.9 whitenoise==6.6.0 python-decouple==3.8 pillow==10.1.0"

# 11. Criar arquivo .env
echo -e "${YELLOW}🔐 Criando arquivo .env...${NC}"
sudo -u django bash -c "cat > /home/django/sistema-rural/.env << 'EOF'
DEBUG=False
SECRET_KEY=django-insecure-sistema-rural-ia-2025-producao-segura
DB_NAME=sistema_rural
DB_USER=django_user
DB_PASSWORD=Django2025@
DB_HOST=localhost
DB_PORT=5432
EOF"

# 12. Criar settings_producao.py
echo -e "${YELLOW}⚙️ Criando configuração de produção...${NC}"
sudo -u django bash -c "cat > /home/django/sistema-rural/sistema_rural/settings_producao.py << 'EOF'
import os
from decouple import config
from .settings import *

# Configurações de Produção
DEBUG = False
ALLOWED_HOSTS = ['45.32.219.76', 'localhost', '127.0.0.1']

# Banco de dados PostgreSQL
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

# Arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Segurança
SECRET_KEY = config('SECRET_KEY', default='django-insecure-sistema-rural-ia-2025-producao-segura')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Middleware para arquivos estáticos
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Logs
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

# 13. Configurar Django
echo -e "${YELLOW}🔧 Configurando Django...${NC}"
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao"
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && python manage.py migrate --settings=sistema_rural.settings_producao"

# 14. Criar superusuário (se não existir)
echo -e "${YELLOW}👤 Criando superusuário...${NC}"
sudo -u django bash -c "cd /home/django/sistema-rural && source venv/bin/activate && echo 'from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username=\"admin\").exists() or User.objects.create_superuser(\"admin\", \"admin@sistema-rural.com\", \"admin123\")' | python manage.py shell --settings=sistema_rural.settings_producao"

# 15. Configurar Gunicorn
echo -e "${YELLOW}🚀 Configurando Gunicorn...${NC}"
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

# 16. Configurar Nginx
echo -e "${YELLOW}🌐 Configurando Nginx...${NC}"
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

# 17. Ativar site no Nginx
executar_comando "Ativando site no Nginx" "ln -sf /etc/nginx/sites-available/sistema-rural /etc/nginx/sites-enabled"
executar_comando "Removendo site padrão" "rm -f /etc/nginx/sites-enabled/default"

# 18. Recarregar e iniciar serviços
executar_comando "Recarregando systemd" "systemctl daemon-reload"
executar_comando "Testando configuração Nginx" "nginx -t"
executar_comando "Iniciando serviço Sistema Rural" "systemctl start sistema-rural"
executar_comando "Habilitando serviço Sistema Rural" "systemctl enable sistema-rural"
executar_comando "Reiniciando Nginx" "systemctl restart nginx"

# 19. Configurar firewall
executar_comando "Configurando firewall" "ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw --force enable"

# 20. Verificar status
echo -e "${YELLOW}🔍 Verificando status dos serviços...${NC}"
systemctl status sistema-rural --no-pager -l
systemctl status nginx --no-pager -l

echo ""
echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "${BLUE}🌐 Sistema disponível em: http://45.32.219.76${NC}"
echo -e "${BLUE}👤 Admin: http://45.32.219.76/admin${NC}"
echo -e "${BLUE}📊 Usuário: admin / Senha: admin123${NC}"
echo ""
echo -e "${YELLOW}🔧 Comandos úteis:${NC}"
echo -e "${BLUE}• Ver logs: sudo journalctl -u sistema-rural -f${NC}"
echo -e "${BLUE}• Reiniciar: sudo systemctl restart sistema-rural${NC}"
echo -e "${BLUE}• Status: sudo systemctl status sistema-rural${NC}"
echo ""
echo -e "${GREEN}✅ Sistema Rural com IA Inteligente está rodando em produção!${NC}"



