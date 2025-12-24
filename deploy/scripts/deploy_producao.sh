#!/bin/bash
# 🚀 SCRIPT DE DEPLOY PARA PRODUÇÃO - MONPEC.COM.BR

echo "🚀 INICIANDO DEPLOY MONPEC.COM.BR"
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute como root: sudo ./deploy_producao.sh"
    exit 1
fi

# 1. ATUALIZAR SISTEMA
log "Atualizando sistema..."
apt update && apt upgrade -y

# 2. INSTALAR DEPENDÊNCIAS
log "Instalando dependências..."
apt install -y nginx postgresql postgresql-contrib python3 python3-pip python3-venv git certbot python3-certbot-nginx htop iotop nethogs

# 3. CONFIGURAR POSTGRESQL
log "Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE monpec_db;"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"

# 4. CRIAR ESTRUTURA DE DIRETÓRIOS
log "Criando estrutura de diretórios..."
mkdir -p /var/www/monpec.com.br
mkdir -p /var/log/monpec
mkdir -p /var/backups
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# 5. CLONAR REPOSITÓRIO
log "Clonando repositório..."
cd /var/www/monpec.com.br
if [ -d ".git" ]; then
    log "Atualizando repositório existente..."
    git pull origin main
else
    log "Clonando repositório pela primeira vez..."
    git clone https://github.com/LMONCAO/Monpec_projetista.git .
fi

# 6. CONFIGURAR AMBIENTE VIRTUAL
log "Configurando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary whitenoise

# 7. CONFIGURAR SETTINGS DE PRODUÇÃO
log "Configurando settings de produção..."
cat > sistema_rural/settings_producao.py << 'EOF'
import os
from .settings import *

# Configurações de produção
DEBUG = False
ALLOWED_HOSTS = ['monpec.com.br', 'www.monpec.com.br', 'localhost', '127.0.0.1']

# Banco de dados PostgreSQL
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

# Configurações de segurança
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Arquivos estáticos
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
            'filename': '/var/log/monpec/django.log',
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

# 8. EXECUTAR MIGRAÇÕES
log "Executando migrações..."
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
python manage.py migrate

# 9. COLETAR ARQUIVOS ESTÁTICOS
log "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 10. CONFIGURAR NGINX
log "Configurando Nginx..."
cat > /etc/nginx/sites-available/monpec.com.br << 'EOF'
server {
    listen 80;
    server_name monpec.com.br www.monpec.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monpec.com.br www.monpec.com.br;
    
    # Certificado SSL (será configurado pelo certbot)
    ssl_certificate /etc/letsencrypt/live/monpec.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monpec.com.br/privkey.pem;
    
    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Logs
    access_log /var/log/nginx/monpec_access.log;
    error_log /var/log/nginx/monpec_error.log;
    
    # Arquivos estáticos
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
    
    # Aplicação Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
EOF

# 11. ATIVAR SITE NO NGINX
log "Ativando site no Nginx..."
ln -sf /etc/nginx/sites-available/monpec.com.br /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 12. CONFIGURAR GUNICORN
log "Configurando Gunicorn..."
cat > /etc/systemd/system/monpec.service << 'EOF'
[Unit]
Description=Monpec Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/monpec.com.br
Environment=DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
ExecStart=/var/www/monpec.com.br/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 sistema_rural.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 13. CONFIGURAR PERMISSÕES
log "Configurando permissões..."
chown -R www-data:www-data /var/www/monpec.com.br
chmod -R 755 /var/www/monpec.com.br

# 14. TESTAR CONFIGURAÇÃO NGINX
log "Testando configuração Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    success "Configuração Nginx OK!"
else
    error "Erro na configuração Nginx!"
    exit 1
fi

# 15. INICIAR SERVIÇOS
log "Iniciando serviços..."
systemctl daemon-reload
systemctl enable monpec
systemctl start monpec
systemctl restart nginx

# 16. CONFIGURAR CERTIFICADO SSL
log "Configurando certificado SSL..."
certbot --nginx -d monpec.com.br -d www.monpec.com.br --non-interactive --agree-tos --email contato@monpec.com.br

# 17. CONFIGURAR BACKUP AUTOMÁTICO
log "Configurando backup automático..."
cat > /usr/local/bin/backup_monpec.sh << 'EOF'
#!/bin/bash
# Backup diário do Monpec
DATE=$(date +%Y%m%d_%H%M%S)

# Backup do banco de dados
pg_dump monpec_db > /var/backups/monpec_db_$DATE.sql

# Backup dos arquivos de mídia
tar -czf /var/backups/monpec_media_$DATE.tar.gz /var/www/monpec.com.br/media/

# Manter apenas backups dos últimos 30 dias
find /var/backups/ -name "monpec_*" -mtime +30 -delete

echo "Backup concluído: $DATE" >> /var/log/monpec/backup.log
EOF

chmod +x /usr/local/bin/backup_monpec.sh

# Adicionar ao crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup_monpec.sh") | crontab -

# 18. VERIFICAR STATUS
log "Verificando status dos serviços..."
systemctl status monpec --no-pager
systemctl status nginx --no-pager

# 19. TESTAR ACESSO
log "Testando acesso..."
sleep 5
curl -I http://localhost:8000

# 20. INFORMAÇÕES FINAIS
echo ""
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=================================="
echo "🌐 URL: https://monpec.com.br"
echo "📊 Status: systemctl status monpec"
echo "📝 Logs: tail -f /var/log/nginx/monpec_access.log"
echo "🔄 Reiniciar: systemctl restart monpec"
echo "📦 Backup: /usr/local/bin/backup_monpec.sh"
echo ""
echo "✅ Sistema pronto para uso!"

