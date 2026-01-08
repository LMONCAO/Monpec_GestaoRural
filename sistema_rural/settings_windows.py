"""
Django settings for sistema_rural project - WINDOWS (Desenvolvimento Local)
Configuração simplificada para desenvolvimento no Windows.
"""
# ⚠️ CRÍTICO: Definir DEBUG e ALLOWED_HOSTS ANTES de importar settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']

# IMPORTANTE: Importar e sobrescrever do settings.py base
from .settings import *

# ⚠️ CRÍTICO: Sobrescrever DEBUG e ALLOWED_HOSTS IMEDIATAMENTE APÓS IMPORTAR
DEBUG = True
ALLOWED_HOSTS = ['*']

# Database - PostgreSQL (obrigatório)
# Usa as configurações do settings.py base que já valida as variáveis de ambiente
# Se necessário, sobrescrever aqui para desenvolvimento local
from decouple import config
import os

DB_NAME = config('DB_NAME', default=None)
DB_USER = config('DB_USER', default=None)
DB_PASSWORD = config('DB_PASSWORD', default=None)
DB_HOST = config('DB_HOST', default='localhost')
DB_PORT = config('DB_PORT', default='5432')

# Validar que todas as variáveis necessárias estão configuradas
if not DB_NAME or not DB_USER or not DB_PASSWORD:
    raise ValueError(
        "Configuração do banco de dados PostgreSQL é obrigatória! "
        "Configure as variáveis DB_NAME, DB_USER e DB_PASSWORD no arquivo .env ou como variáveis de ambiente."
    )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,
    }
}

# Security - Desabilitado para desenvolvimento
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Logging - Apenas console (sem arquivo)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Static files (Windows)
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# CSRF - adicionar IPs locais
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://192.168.100.91:8000',
    'http://0.0.0.0:8000',
]

# ⚠️ FORÇAR NOVAMENTE NO FINAL - GARANTIR
DEBUG = True
ALLOWED_HOSTS = ['*']
