#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Deploy em Produção - Sistema Rural com IA
Servidor: 45.32.219.76
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def executar_comando(comando, descricao):
    """Executa comando e exibe resultado"""
    print(f"\n🔄 {descricao}")
    print(f"Comando: {comando}")
    try:
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Sucesso: {resultado.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e.stderr}")
        return False

def preparar_producao():
    """Prepara o sistema para produção"""
    print("🚀 PREPARANDO SISTEMA PARA PRODUÇÃO")
    print("=" * 50)
    
    # 1. Verificar se estamos no diretório correto
    if not os.path.exists('manage.py'):
        print("❌ Erro: Execute este script no diretório raiz do projeto Django")
        return False
    
    # 2. Instalar dependências de produção
    print("\n📦 Instalando dependências de produção...")
    dependencias_producao = [
        'gunicorn',
        'psycopg2-binary',  # Para PostgreSQL em produção
        'whitenoise',       # Para servir arquivos estáticos
        'python-decouple',  # Para variáveis de ambiente
    ]
    
    for dep in dependencias_producao:
        if not executar_comando(f"pip install {dep}", f"Instalando {dep}"):
            print(f"⚠️ Aviso: Falha ao instalar {dep}")
    
    # 3. Criar arquivo requirements.txt para produção
    print("\n📝 Criando requirements.txt para produção...")
    with open('requirements_producao.txt', 'w') as f:
        f.write("""# Sistema Rural com IA - Dependências de Produção
Django==4.2.7
gunicorn==21.2.0
psycopg2-binary==2.9.9
whitenoise==6.6.0
python-decouple==3.8
pillow==10.1.0
""")
    
    # 4. Criar configuração de produção
    print("\n⚙️ Criando configuração de produção...")
    config_producao = """
# settings_producao.py
import os
from decouple import config

# Configurações de Produção
DEBUG = False
ALLOWED_HOSTS = ['45.32.219.76', 'localhost', '127.0.0.1']

# Banco de dados PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='sistema_rural'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Segurança
SECRET_KEY = config('SECRET_KEY', default='sua-chave-secreta-super-segura')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'sistema_rural.log',
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
"""
    
    with open('sistema_rural/settings_producao.py', 'w') as f:
        f.write(config_producao)
    
    # 5. Criar arquivo .env para variáveis de ambiente
    print("\n🔐 Criando arquivo .env...")
    env_content = """# Configurações de Produção
DEBUG=False
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DB_NAME=sistema_rural
DB_USER=postgres
DB_PASSWORD=sua-senha-postgres
DB_HOST=localhost
DB_PORT=5432
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # 6. Criar script de deploy
    print("\n📜 Criando script de deploy...")
    deploy_script = """#!/bin/bash
# Script de Deploy para Produção

echo "🚀 Iniciando Deploy do Sistema Rural com IA"

# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências do sistema
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx

# 3. Configurar PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE sistema_rural;"
sudo -u postgres psql -c "CREATE USER django_user WITH PASSWORD 'sua_senha_segura';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sistema_rural TO django_user;"

# 4. Criar usuário para a aplicação
sudo useradd -m -s /bin/bash django
sudo usermod -aG sudo django

# 5. Clonar projeto (substitua pela URL do seu repositório)
cd /home/django
sudo -u django git clone https://github.com/seu-usuario/sistema-rural.git
cd sistema-rural

# 6. Configurar ambiente virtual
sudo -u django python3 -m venv venv
sudo -u django source venv/bin/activate
sudo -u django pip install -r requirements_producao.txt

# 7. Configurar Django
sudo -u django python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao
sudo -u django python manage.py migrate --settings=sistema_rural.settings_producao

# 8. Configurar Gunicorn
sudo -u django echo '[Unit]
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
WantedBy=multi-user.target' > /etc/systemd/system/sistema-rural.service

# 9. Configurar Nginx
sudo -u django echo 'server {
    listen 80;
    server_name 45.32.219.76;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/django/sistema-rural;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/sistema-rural/sistema_rural.sock;
    }
}' > /etc/nginx/sites-available/sistema-rural

# 10. Ativar serviços
sudo ln -s /etc/nginx/sites-available/sistema-rural /etc/nginx/sites-enabled
sudo systemctl daemon-reload
sudo systemctl start sistema-rural
sudo systemctl enable sistema-rural
sudo systemctl restart nginx

echo "✅ Deploy concluído! Sistema disponível em http://45.32.219.76"
"""
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_script)
    
    # 7. Tornar script executável
    os.chmod('deploy.sh', 0o755)
    
    print("\n✅ SISTEMA PREPARADO PARA PRODUÇÃO!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Faça upload dos arquivos para o servidor")
    print("2. Execute: ssh root@45.32.219.76")
    print("3. Execute: chmod +x deploy.sh && ./deploy.sh")
    print("4. Configure as variáveis de ambiente no arquivo .env")
    print("5. Reinicie os serviços: sudo systemctl restart sistema-rural nginx")
    
    return True

if __name__ == "__main__":
    preparar_producao()



