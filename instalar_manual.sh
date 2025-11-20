#!/bin/bash

echo "🚀 INSTALAÇÃO MANUAL DO MONPEC"
echo "=============================="

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

# 7. Criar arquivos Django básicos
echo "📝 Criando arquivos Django básicos..."

# Criar manage.py
cat > manage.py << 'EOF'
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
EOF

# Criar estrutura básica do projeto
mkdir -p sistema_rural
mkdir -p gestao_rural
mkdir -p templates

# Criar settings.py básico
cat > sistema_rural/__init__.py << 'EOF'
EOF

cat > sistema_rural/settings.py << 'EOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-monpec-2025-key'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestao_rural',
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

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EOF

# Criar urls.py básico
cat > sistema_rural/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <html>
    <head><title>Monpec - Sistema Rural</title></head>
    <body>
        <h1>🚀 Monpec - Sistema Rural</h1>
        <p>Sistema funcionando!</p>
        <p><a href="/admin/">Admin</a></p>
    </body>
    </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]
EOF

# Criar wsgi.py
cat > sistema_rural/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
application = get_wsgi_application()
EOF

# Criar asgi.py
cat > sistema_rural/asgi.py << 'EOF'
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
application = get_asgi_application()
EOF

# Criar app básico
cat > gestao_rural/__init__.py << 'EOF'
EOF

cat > gestao_rural/apps.py << 'EOF'
from django.apps import AppConfig

class GestaoRuralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestao_rural'
EOF

cat > gestao_rural/models.py << 'EOF'
from django.db import models

class Produtor(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    
    def __str__(self):
        return self.nome
EOF

cat > gestao_rural/admin.py << 'EOF'
from django.contrib import admin
from .models import Produtor

@admin.register(Produtor)
class ProdutorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone']
EOF

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

# 11. Iniciar servidor
echo "🚀 Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000 &

echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "🌐 Acesse: http://191.252.225.106:8000"
echo "👤 Login: admin / 123456"

