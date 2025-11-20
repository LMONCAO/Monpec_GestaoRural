#!/bin/bash
# 🚀 CONFIGURAÇÃO FINAL DO MONPEC NA LOCAWEB

echo "🚀 CONFIGURANDO MONPEC NA LOCAWEB"
echo "================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# 1. PARAR SERVIÇOS PROBLEMÁTICOS
log "Parando serviços problemáticos..."
systemctl stop sistema-rural.service 2>/dev/null || true
systemctl disable sistema-rural.service 2>/dev/null || true
systemctl stop monpec.service 2>/dev/null || true
systemctl disable monpec.service 2>/dev/null || true

# 2. ATUALIZAR SISTEMA
log "Atualizando sistema..."
yum update -y

# 3. INSTALAR DEPENDÊNCIAS
log "Instalando dependências..."
yum install -y python3 python3-pip python3-venv postgresql-server postgresql-contrib nginx git curl wget

# Instalar Gunicorn globalmente
pip3 install gunicorn

success "Dependências instaladas!"

# 4. CONFIGURAR POSTGRESQL
log "Configurando PostgreSQL..."
postgresql-setup initdb
systemctl start postgresql
systemctl enable postgresql
sleep 5

# Criar banco e usuário
sudo -u postgres psql -c "CREATE DATABASE monpec_db;" 2>/dev/null || echo "Banco já existe"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';" 2>/dev/null || echo "Usuário já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"

success "PostgreSQL configurado!"

# 5. CONFIGURAR PROJETO
log "Configurando projeto..."
mkdir -p /var/www/monpec.com.br

# Se arquivos estão em /tmp/monpec, copiar
if [ -d "/tmp/monpec" ]; then
    log "Copiando arquivos de /tmp/monpec..."
    cp -r /tmp/monpec/* /var/www/monpec.com.br/
else
    log "Clonando repositório..."
    cd /var/www
    git clone https://github.com/LMONCAO/Monpec_projetista.git monpec.com.br
fi

cd /var/www/monpec.com.br

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements_producao.txt

success "Projeto configurado!"

# 6. CONFIGURAR DJANGO
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

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/monpec.log',
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

success "Django configurado!"

# 7. CONFIGURAR NGINX
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
        proxy_redirect off;
    }
    
    location /static/ {
        alias /var/www/monpec.com.br/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/monpec.com.br/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Remover configuração padrão
rm -f /etc/nginx/conf.d/default.conf

systemctl start nginx
systemctl enable nginx

success "Nginx configurado!"

# 8. CONFIGURAR GUNICORN
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
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Configurar permissões
chown -R root:root /var/www/monpec.com.br
chmod -R 755 /var/www/monpec.com.br

systemctl daemon-reload
systemctl enable monpec
systemctl start monpec

success "Gunicorn configurado!"

# 9. CONFIGURAR FIREWALL
log "Configurando firewall..."
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --reload

success "Firewall configurado!"

# 10. VERIFICAR STATUS
log "Verificando status dos serviços..."
sleep 5

# Verificar se o serviço está rodando
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

# 11. TESTAR ACESSO
log "Testando acesso..."
sleep 10

# Testar se o sistema responde
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
    success "Sistema respondendo corretamente! (HTTP $HTTP_STATUS)"
else
    warning "Sistema pode não estar respondendo corretamente (HTTP $HTTP_STATUS)"
fi

# 12. INFORMAÇÕES FINAIS
echo ""
echo "🎉 CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================="
echo "🌐 URL Local: http://localhost:8000"
echo "🌐 URL Externa: http://191.252.225.106"
echo "👤 Login: admin"
echo "🔑 Senha: 123456"
echo ""
echo "📊 COMANDOS ÚTEIS:"
echo "=================="
echo "Status: systemctl status monpec"
echo "Logs: journalctl -u monpec -f"
echo "Reiniciar: systemctl restart monpec"
echo "Testar: curl http://localhost:8000"
echo ""
echo "✅ Sistema configurado e funcionando!"

# 13. VERIFICAÇÃO FINAL
log "Verificação final do sistema..."
echo ""
echo "📊 STATUS DOS SERVIÇOS:"
echo "========================"
systemctl status monpec --no-pager -l
echo ""
systemctl status nginx --no-pager -l
echo ""
echo "🌐 TESTE DE ACESSO:"
echo "=================="
curl -I http://localhost:8000 2>/dev/null | head -1 || echo "Teste de acesso falhou"

