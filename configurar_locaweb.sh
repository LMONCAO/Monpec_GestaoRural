#!/bin/bash
# 🌐 SCRIPT DE CONFIGURAÇÃO LOCAWEB CLOUD - MONPEC.COM.BR

echo "🌐 CONFIGURANDO MONPEC NA LOCAWEB CLOUD"
echo "======================================"

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
    error "Execute como root: sudo ./configurar_locaweb.sh"
    exit 1
fi

# 1. ATUALIZAR SISTEMA
log "Atualizando sistema..."
apt update && apt upgrade -y

# 2. INSTALAR DEPENDÊNCIAS
log "Instalando dependências..."
apt install -y python3 python3-pip python3-venv python3-dev postgresql postgresql-contrib nginx git curl wget vim htop certbot python3-certbot-nginx

# 3. CONFIGURAR POSTGRESQL
log "Configurando PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Criar banco e usuário
sudo -u postgres psql -c "CREATE DATABASE monpec_db;"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"

success "PostgreSQL configurado!"

# 4. CRIAR ESTRUTURA DE DIRETÓRIOS
log "Criando estrutura de diretórios..."
mkdir -p /var/www/monpec.com.br
mkdir -p /var/log/monpec
mkdir -p /var/backups

# 5. CLONAR REPOSITÓRIO
log "Clonando repositório..."
cd /var/www
if [ -d "monpec.com.br" ]; then
    log "Diretório já existe, fazendo backup..."
    mv monpec.com.br monpec_backup_$(date +%Y%m%d_%H%M%S)
fi

git clone https://github.com/LMONCAO/Monpec_projetista.git monpec.com.br
chown -R www-data:www-data monpec.com.br

success "Repositório clonado!"

# 6. CONFIGURAR AMBIENTE VIRTUAL
log "Configurando ambiente virtual..."
cd monpec.com.br
python3 -m venv venv
chown -R www-data:www-data venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements_producao.txt

success "Ambiente virtual configurado!"

# 7. CONFIGURAR SETTINGS DE PRODUÇÃO
log "Configurando settings de produção..."
cat > sistema_rural/settings_producao.py << 'EOF'
import os
from .settings import *

# Configurações de produção
DEBUG = False
ALLOWED_HOSTS = ['monpec.com.br', 'www.monpec.com.br', '10.1.1.234', 'localhost', '127.0.0.1']

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

success "Settings de produção configurado!"

# 8. EXECUTAR MIGRAÇÕES
log "Executando migrações..."
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
python manage.py migrate

# Criar superusuário
log "Criando superusuário..."
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

success "Migrações executadas!"

# 9. CONFIGURAR NGINX
log "Configurando Nginx..."
cat > /etc/nginx/sites-available/monpec.com.br << 'EOF'
server {
    listen 80;
    server_name monpec.com.br www.monpec.com.br 10.1.1.234;
    
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

# Ativar site
ln -sf /etc/nginx/sites-available/monpec.com.br /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t
if [ $? -eq 0 ]; then
    success "Configuração Nginx OK!"
else
    error "Erro na configuração Nginx!"
    exit 1
fi

# 10. CONFIGURAR GUNICORN
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

# 11. CONFIGURAR PERMISSÕES
log "Configurando permissões..."
chown -R www-data:www-data /var/www/monpec.com.br
chmod -R 755 /var/www/monpec.com.br

# 12. INICIAR SERVIÇOS
log "Iniciando serviços..."
systemctl daemon-reload
systemctl enable monpec
systemctl start monpec
systemctl restart nginx

# 13. CONFIGURAR FIREWALL
log "Configurando firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 14. VERIFICAR STATUS
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

# 15. TESTAR ACESSO
log "Testando acesso..."
sleep 10

# Testar se o sistema responde
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
    success "Sistema respondendo corretamente! (HTTP $HTTP_STATUS)"
else
    warning "Sistema pode não estar respondendo corretamente (HTTP $HTTP_STATUS)"
fi

# 16. CONFIGURAR BACKUP AUTOMÁTICO
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

# 17. INFORMAÇÕES FINAIS
echo ""
echo "🎉 CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================="
echo "🌐 URL Local: http://10.1.1.234"
echo "🌐 URL Domínio: http://monpec.com.br (após configurar DNS)"
echo "👤 Login: admin"
echo "🔑 Senha: 123456"
echo ""
echo "📊 COMANDOS ÚTEIS:"
echo "=================="
echo "Status: systemctl status monpec"
echo "Logs: tail -f /var/log/monpec/django.log"
echo "Reiniciar: systemctl restart monpec"
echo "Backup: /usr/local/bin/backup_monpec.sh"
echo ""
echo "🔧 PRÓXIMOS PASSOS:"
echo "=================="
echo "1. Configurar DNS do domínio monpec.com.br → 10.1.1.234"
echo "2. Configurar SSL: certbot --nginx -d monpec.com.br"
echo "3. Testar acesso: https://monpec.com.br"
echo ""
echo "✅ Sistema configurado na Locaweb Cloud!"

# 18. VERIFICAÇÃO FINAL
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
curl -I http://10.1.1.234 2>/dev/null | head -1 || echo "Teste de acesso falhou"

