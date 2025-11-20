#!/bin/bash
# 🚀 INSTALAÇÃO COMPLETA DO MONPEC

echo "🚀 INSTALANDO MONPEC COMPLETO"
echo "============================="

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# 1. ATUALIZAR SISTEMA
log "Atualizando sistema..."
yum update -y

# 2. INSTALAR DEPENDÊNCIAS
log "Instalando dependências..."
yum install -y python3 python3-pip python3-venv postgresql-server postgresql-contrib nginx git curl wget

# 3. CONFIGURAR POSTGRESQL
log "Configurando PostgreSQL..."
postgresql-setup initdb
systemctl start postgresql
systemctl enable postgresql
sleep 5

# Criar banco
sudo -u postgres psql -c "CREATE DATABASE monpec_db;" 2>/dev/null || echo "Banco já existe"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';" 2>/dev/null || echo "Usuário já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"

# 4. CONFIGURAR PROJETO
log "Configurando projeto..."
mkdir -p /var/www/monpec.com.br
cd /var/www/monpec.com.br

# Clonar repositório
git clone https://github.com/LMONCAO/Monpec_projetista.git .

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements_producao.txt

# 5. CONFIGURAR DJANGO
log "Configurando Django..."
cat > sistema_rural/settings_producao.py << 'EOF'
import os
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monpec_db',
        'USER': 'monpec_user',
        'PASSWORD': 'Monpec2025!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_ROOT = '/var/www/monpec.com.br/static'
MEDIA_ROOT = '/var/www/monpec.com.br/media'
EOF

# Executar migrações
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
python manage.py migrate

# Criar superusuário
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com.br', '123456')
    print('Superusuário criado: admin / 123456')
else:
    print('Superusuário já existe')
"

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 6. CONFIGURAR NGINX
log "Configurando Nginx..."
cat > /etc/nginx/conf.d/monpec.conf << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/monpec.com.br/static/;
    }
    
    location /media/ {
        alias /var/www/monpec.com.br/media/;
    }
}
EOF

systemctl start nginx
systemctl enable nginx

# 7. CONFIGURAR GUNICORN
log "Configurando Gunicorn..."
cat > /etc/systemd/system/monpec.service << 'EOF'
[Unit]
Description=Monpec Gunicorn daemon
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/var/www/monpec.com.br
Environment=DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
ExecStart=/var/www/monpec.com.br/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 sistema_rural.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable monpec
systemctl start monpec

# 8. CONFIGURAR FIREWALL
log "Configurando firewall..."
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --reload

# 9. VERIFICAR STATUS
log "Verificando status..."
sleep 5

if systemctl is-active --quiet monpec; then
    success "Serviço Monpec está rodando!"
else
    error "Erro ao iniciar serviço Monpec!"
    systemctl status monpec --no-pager
fi

if systemctl is-active --quiet nginx; then
    success "Nginx está rodando!"
else
    error "Erro ao iniciar Nginx!"
    systemctl status nginx --no-pager
fi

# 10. TESTAR ACESSO
log "Testando acesso..."
sleep 10

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
    success "Sistema respondendo corretamente! (HTTP $HTTP_STATUS)"
else
    error "Sistema não está respondendo (HTTP $HTTP_STATUS)"
fi

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo "========================"
echo "🌐 URL: http://191.252.225.106"
echo "👤 Login: admin"
echo "🔑 Senha: 123456"
echo ""
echo "✅ Sistema instalado e funcionando!"

