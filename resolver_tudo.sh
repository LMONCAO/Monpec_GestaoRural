#!/bin/bash

echo "🚀 RESOLVENDO TODOS OS PROBLEMAS DO MONPEC"
echo "=========================================="

# 1. Criar diretório
echo "📁 Criando diretório..."
mkdir -p /var/www/monpec.com.br
cd /var/www/monpec.com.br

# 2. Instalar PostgreSQL
echo "🗄️ Instalando PostgreSQL..."
yum install -y postgresql postgresql-server postgresql-devel
postgresql-setup initdb
systemctl start postgresql
systemctl enable postgresql

# 3. Configurar PostgreSQL
echo "🔐 Configurando banco de dados..."
sudo -u postgres psql -c "CREATE DATABASE monpec_db;" 2>/dev/null || echo "Banco já existe"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';" 2>/dev/null || echo "Usuário já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"
sudo -u postgres psql -c "ALTER USER monpec_user CREATEDB;"

# 4. Instalar dependências Python
echo "🐍 Instalando dependências Python..."
yum install -y python3 python3-pip python3-devel gcc
pip3 install django psycopg2-binary gunicorn pillow reportlab

# 5. Criar ambiente virtual
echo "🔧 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# 6. Instalar dependências no venv
echo "📦 Instalando dependências no venv..."
pip install django psycopg2-binary gunicorn pillow reportlab

# 7. Configurar Django
echo "⚙️ Configurando Django..."
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao

# 8. Executar migrações
echo "🔄 Executando migrações..."
python manage.py makemigrations
python manage.py migrate

# 9. Criar superusuário
echo "👤 Criando superusuário..."
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@monpec.com.br', '123456')" | python manage.py shell

# 10. Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 11. Instalar e configurar Nginx
echo "🌐 Configurando Nginx..."
yum install -y nginx
systemctl start nginx
systemctl enable nginx

# 12. Configurar Nginx
cat > /etc/nginx/conf.d/monpec.com.br.conf << 'EOF'
server {
    listen 80;
    server_name monpec.com.br www.monpec.com.br 191.252.225.106;

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

# 13. Configurar Gunicorn
echo "🔧 Configurando Gunicorn..."
cat > /var/www/monpec.com.br/gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 3
user = "root"
group = "root"
daemon = False
pidfile = "/var/run/gunicorn.pid"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
EOF

# 14. Criar serviço systemd
echo "⚙️ Configurando serviço..."
cat > /etc/systemd/system/monpec.service << 'EOF'
[Unit]
Description=Monpec Django Application
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/var/www/monpec.com.br
Environment="DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao"
ExecStart=/var/www/monpec.com.br/venv/bin/gunicorn --config gunicorn.conf.py sistema_rural.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 15. Criar diretórios de log
mkdir -p /var/log/gunicorn

# 16. Configurar firewall
echo "🔥 Configurando firewall..."
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload

# 17. Iniciar serviços
echo "🚀 Iniciando serviços..."
systemctl daemon-reload
systemctl start nginx
systemctl enable nginx
systemctl start monpec
systemctl enable monpec

# 18. Verificar status
echo "📊 Verificando status dos serviços..."
systemctl status nginx --no-pager
systemctl status monpec --no-pager

# 19. Testar aplicação
echo "🧪 Testando aplicação..."
curl -I http://localhost:8000 || echo "Erro ao testar aplicação"

echo "✅ INSTALAÇÃO COMPLETA!"
echo "🌐 Acesse: http://191.252.225.106"
echo "👤 Login: admin / 123456"

