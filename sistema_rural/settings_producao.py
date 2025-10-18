# -*- coding: utf-8 -*-
"""
Configurações de Produção - Sistema Rural com IA
Servidor: 45.32.219.76
"""

import os
from decouple import config
from .settings import *

# ==================== CONFIGURAÇÕES DE PRODUÇÃO ====================

# Modo de debug desabilitado
DEBUG = False

# Hosts permitidos
ALLOWED_HOSTS = [
    '45.32.219.76',
    'localhost',
    '127.0.0.1',
    'sistema-rural.local'
]

# ==================== BANCO DE DADOS ====================

# PostgreSQL para produção
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='sistema_rural'),
        'USER': config('DB_USER', default='django_user'),
        'PASSWORD': config('DB_PASSWORD', default='Django2025@'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        }
    }
}

# ==================== ARQUIVOS ESTÁTICOS ====================

# Configuração de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise para servir arquivos estáticos
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware para arquivos estáticos
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# ==================== SEGURANÇA ====================

# Chave secreta
SECRET_KEY = config('SECRET_KEY', default='django-insecure-sistema-rural-ia-2025-producao-segura')

# Configurações de segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS (descomentar quando configurar SSL)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# ==================== LOGS ====================

# Configuração de logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/django/sistema-rural/sistema_rural.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
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

# ==================== CACHE ====================

# Cache em memória para produção
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# ==================== EMAIL ====================

# Configuração de email (se necessário)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ==================== PERFORMANCE ====================

# Configurações de performance
CONN_MAX_AGE = 60

# Sessões
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = False

# ==================== IA E SISTEMA INTELIGENTE ====================

# Configurações específicas para IA
IA_CONFIG = {
    'ENABLE_AI': True,
    'AI_MODEL_PATH': '/home/django/sistema-rural/ia_models/',
    'AI_LOG_LEVEL': 'INFO',
    'AI_CACHE_TTL': 3600,  # 1 hora
}

# ==================== BACKUP ====================

# Configurações de backup automático
BACKUP_CONFIG = {
    'ENABLE_AUTO_BACKUP': True,
    'BACKUP_DIR': '/home/django/backups/',
    'BACKUP_RETENTION_DAYS': 30,
    'BACKUP_TIME': '02:00',  # 2:00 AM
}

# ==================== MONITORAMENTO ====================

# Configurações de monitoramento
MONITORING_CONFIG = {
    'ENABLE_METRICS': True,
    'METRICS_PORT': 8001,
    'HEALTH_CHECK_ENDPOINT': '/health/',
}

# ==================== FIM DAS CONFIGURAÇÕES ====================

print("🚀 Sistema Rural com IA - Configuração de Produção Carregada")
print(f"🌐 Hosts permitidos: {ALLOWED_HOSTS}")
print(f"🗄️ Banco de dados: {DATABASES['default']['NAME']}")
print(f"📁 Arquivos estáticos: {STATIC_ROOT}")
print(f"🤖 IA habilitada: {IA_CONFIG['ENABLE_AI']}")
print("✅ Configuração de produção ativa!")



