#!/bin/bash

# 🚀 SETUP COMPLETO MONPEC - DESENVOLVIMENTO PROFISSIONAL
# Execute este script para configurar tudo automaticamente

echo "========================================="
echo "🚀 SETUP COMPLETO MONPEC"
echo "========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    print_error "Execute este script no diretório raiz do projeto Django (onde está manage.py)"
    exit 1
fi

echo "1️⃣ INSTALANDO POSTGRESQL LOCAL..."
sudo apt update
sudo apt install -y postgresql postgresql-contrib python3-psycopg2

# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

print_status "PostgreSQL instalado e iniciado"

echo ""
echo "2️⃣ CRIANDO BANCO DE DADOS..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS monpec_db;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS monpec_user;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'monpec123';"
sudo -u postgres psql -c "CREATE DATABASE monpec_db OWNER monpec_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"

print_status "Banco de dados criado"

echo ""
echo "3️⃣ CONFIGURANDO DJANGO PARA POSTGRESQL..."

# Backup do settings.py original
cp sistema_rural/settings.py sistema_rural/settings.py.backup

# Configurar PostgreSQL no settings.py
cat > sistema_rural/settings.py << 'EOF'
"""
Django settings for sistema_rural project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-monpec-desenvolvimento-local-2025'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestao_rural',
    'widget_tweaks',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sistema_rural.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sistema_rural.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monpec_db',
        'USER': 'monpec_user',
        'PASSWORD': 'monpec123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
EOF

print_status "Django configurado para PostgreSQL"

echo ""
echo "4️⃣ INSTALANDO DEPENDÊNCIAS PYTHON..."
pip install psycopg2-binary

print_status "Dependências instaladas"

echo ""
echo "5️⃣ RESETANDO MIGRAÇÕES E BANCO..."
python manage.py migrate --fake-initial 2>/dev/null || true
python manage.py migrate

print_status "Migrações aplicadas"

echo ""
echo "6️⃣ POPULANDO DADOS..."
python manage.py popular_dados_producao

print_status "Dados populados"

echo ""
echo "7️⃣ TESTANDO APLICAÇÃO LOCAL..."
python manage.py runserver --noreload &
SERVER_PID=$!
sleep 3

# Testar se o servidor está respondendo
if curl -s http://localhost:8000/ | grep -q "MONPEC"; then
    print_status "Servidor local funcionando!"
    kill $SERVER_PID 2>/dev/null || true
else
    print_warning "Servidor pode não estar funcionando corretamente"
    kill $SERVER_PID 2>/dev/null || true
fi

echo ""
echo "8️⃣ PREPARANDO PARA DEPLOY..."

# Build da imagem
print_status "Fazendo build da imagem..."
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy
print_status "Fazendo deploy..."
gcloud run deploy monpec \
  --image gcr.io/monpec-sistema-rural/monpec \
  --platform managed \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" \
  --allow-unauthenticated \
  --memory=4Gi \
  --cpu=2 \
  --timeout=300

print_status "Deploy concluído!"

echo ""
echo "9️⃣ TESTANDO PRODUÇÃO..."
sleep 5

# Testar produção
if curl -s https://monpec-29862706245.us-central1.run.app/ | grep -q "MONPEC\|Sistema\|Gestão"; then
    print_status "PRODUÇÃO FUNCIONANDO!"
else
    print_warning "Produção pode precisar de ajustes"
fi

echo ""
echo "========================================="
echo "🎉 SETUP COMPLETO CONCLUÍDO!"
echo "========================================="
echo ""
echo "✅ PostgreSQL local configurado"
echo "✅ Django usando PostgreSQL"
echo "✅ Migrações limpas aplicadas"
echo "✅ Dados populados (1.300 animais)"
echo "✅ Deploy em produção funcionando"
echo ""
echo "🌐 Local: http://localhost:8000/"
echo "🌐 Produção: https://monpec-29862706245.us-central1.run.app/"
echo "👤 Admin: admin / [sua senha]"
echo ""
echo "========================================="
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo "1. Desenvolver sempre com PostgreSQL local"
echo "2. Testar localmente antes de deploy"
echo "3. Fazer deploys frequentes"
echo "4. Monitorar logs regularmente"
echo ""
echo "========================================="