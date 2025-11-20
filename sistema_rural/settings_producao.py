"""
Django settings for sistema_rural project - PRODUÇÃO LOCAWEB

Configurações específicas para produção no servidor Locaweb.
"""
import os
from .settings import *

# Configurações de produção
DEBUG = False

ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    '10.1.1.234',  # IP da VM Locaweb
    'localhost',
    '127.0.0.1',
    '0.0.0.0',  # Permite acesso de qualquer IP na rede
]

# Configuração CSRF para produção
CSRF_TRUSTED_ORIGINS = [
    'https://monpec.com.br',
    'https://www.monpec.com.br',
    'http://10.1.1.234',
    'http://10.1.1.234:8000',  # IP com porta para acesso direto
    'http://localhost:8000',
]

# Banco de dados PostgreSQL para produção
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'monpec_db'),
        'USER': os.getenv('DB_USER', 'monpec_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'Monpec2025!'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Configurações de segurança
# ⚠️ ATENÇÃO: Desabilitado temporariamente para permitir acesso HTTP pelo celular
# Reative quando configurar SSL corretamente
SECURE_SSL_REDIRECT = False  # Era True - desabilitado para acesso pelo celular
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Arquivos estáticos e mídia
STATIC_ROOT = '/var/www/monpec.com.br/static'
MEDIA_ROOT = '/var/www/monpec.com.br/media'

# Configuração de logs
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/monpec/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'gestao_rural': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# URLs do Stripe para produção
STRIPE_SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL', 'https://monpec.com.br/assinaturas/sucesso/')
STRIPE_CANCEL_URL = os.getenv('STRIPE_CANCEL_URL', 'https://monpec.com.br/assinaturas/cancelado/')

# Cache para produção (usando Redis se disponível, senão memória)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Sessões
# ⚠️ ATENÇÃO: Desabilitado temporariamente para permitir acesso HTTP pelo celular
# Reative quando configurar SSL corretamente
SESSION_COOKIE_SECURE = False  # Era True - desabilitado para acesso HTTP
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # Era True - desabilitado para acesso HTTP
CSRF_COOKIE_HTTPONLY = True
