# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

# 1. FORÇAR O AMBIENTE A ACEITAR O CAMINHO COM ACENTO
os.environ["PYTHONIOENCODING"] = "utf-8"

# 2. CAMINHO DO PROJETO (Tratando o erro de Unicode no Windows)
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. CONFIGURAÇÕES BÁSICAS
DEBUG = False
SECRET_KEY = 'django-insecure-chave-temporaria-para-uso-local'
ALLOWED_HOSTS = ['*']

# 4. IMPORTAR AS CONFIGURAÇÕES PADRÃO (Certifique-se que o arquivo settings.py existe na mesma pasta)
try:
    from .settings import *
except ImportError:
    pass

# 5. BANCO DE DADOS (Configuração Direta para evitar o Erro 500)
# Ajuste o NAME, USER e PASSWORD conforme o seu PostgreSQL local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sistema_rural', 
        'USER': 'postgres',
        'PASSWORD': 'sua_senha_aqui', # <-- COLOQUE SUA SENHA DO POSTGRES AQUI
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'client_encoding': 'UTF8',
        }
    }
}

# 6. ARQUIVOS ESTÁTICOS (WhiteNoise)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# 7. DESATIVAR SEGURANÇA RESTRITA (Para funcionar em localhost sem HTTPS)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False