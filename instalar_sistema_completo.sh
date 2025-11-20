#!/bin/bash

echo "🚀 INSTALANDO SISTEMA MONPEC COMPLETO"
echo "====================================="

# Parar serviços existentes
echo "📋 Parando serviços existentes..."
systemctl stop monpec 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
systemctl stop postgresql 2>/dev/null || true

# Atualizar sistema
echo "📦 Atualizando sistema..."
yum update -y
yum install -y epel-release

# Instalar dependências
echo "🔧 Instalando dependências..."
yum install -y python3 python3-pip python3-devel gcc postgresql postgresql-server postgresql-devel nginx git

# Inicializar PostgreSQL
echo "🗄️ Configurando PostgreSQL..."
postgresql-setup initdb
systemctl start postgresql
systemctl enable postgresql

# Configurar PostgreSQL
echo "🔐 Configurando banco de dados..."
sudo -u postgres psql -c "CREATE DATABASE monpec_db;" 2>/dev/null || echo "Banco já existe"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';" 2>/dev/null || echo "Usuário já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"
sudo -u postgres psql -c "ALTER USER monpec_user CREATEDB;"

# Configurar diretório
echo "📁 Configurando diretório..."
mkdir -p /var/www/monpec.com.br
cd /var/www/monpec.com.br

# Verificar se arquivos foram transferidos
echo "📋 Verificando arquivos..."
ls -la

# Criar ambiente virtual
echo "🐍 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install django psycopg2-binary gunicorn pillow reportlab

# Configurar Django
echo "⚙️ Configurando Django..."
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao

# Executar migrações
echo "🔄 Executando migrações..."
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
echo "👤 Criando superusuário..."
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@monpec.com.br', '123456')" | python manage.py shell

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Configurar Nginx
echo "🌐 Configurando Nginx..."
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

# Configurar Gunicorn
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

# Criar serviço systemd
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

# Criar diretórios de log
mkdir -p /var/log/gunicorn

# Configurar firewall
echo "🔥 Configurando firewall..."
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload

# Iniciar serviços
echo "🚀 Iniciando serviços..."
systemctl daemon-reload
systemctl start nginx
systemctl enable nginx
systemctl start monpec
systemctl enable monpec

# Verificar status
echo "📊 Verificando status dos serviços..."
systemctl status nginx --no-pager
systemctl status monpec --no-pager

# Testar aplicação
echo "🧪 Testando aplicação..."
curl -I http://localhost:8000 || echo "Erro ao testar aplicação"

echo "✅ INSTALAÇÃO COMPLETA!"
echo "🌐 Acesse: http://191.252.225.106"
echo "👤 Login: admin / 123456"


