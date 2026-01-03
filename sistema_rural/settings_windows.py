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

# Database - usar SQLite para desenvolvimento
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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
