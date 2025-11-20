"""
Django settings for sistema_rural project - GOOGLE CLOUD PLATFORM

Configurações específicas para produção no Google Cloud Platform.
Suporta Cloud Run, App Engine e Compute Engine.
"""
import os
from .settings import *

# Detectar se está rodando no Google Cloud
IS_GAE = os.getenv('GAE_ENV') is not None
IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None

# Configurações de produção
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS para Google Cloud
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    'monpec-sistema-rural.uc.r.appspot.com',  # App Engine
    'localhost',
    '127.0.0.1',
]

# Adicionar host do Cloud Run se disponível
if IS_CLOUD_RUN:
    # Cloud Run automaticamente define variáveis de ambiente
    # Podemos obter a URL do serviço via variável de ambiente ou request
    # Por enquanto, vamos permitir qualquer subdomínio .a.run.app
    # O Django não suporta wildcards, então vamos usar uma função customizada
    cloud_run_host = os.getenv('CLOUD_RUN_HOST', '')
    if cloud_run_host:
        ALLOWED_HOSTS.append(cloud_run_host)
    # Adicionar hosts comuns do Cloud Run (será expandido dinamicamente)
    # Nota: Django não suporta wildcards, então vamos validar no middleware se necessário

# Configuração CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://monpec.com.br',
    'https://www.monpec.com.br',
    'https://monpec-sistema-rural.uc.r.appspot.com',
]

# Adicionar origem do Cloud Run
if IS_CLOUD_RUN:
    cloud_run_host = os.getenv('CLOUD_RUN_HOST', '')
    if cloud_run_host:
        CSRF_TRUSTED_ORIGINS.append(f'https://{cloud_run_host}')

# Banco de dados - Cloud SQL via Unix Socket (App Engine/Cloud Run)
if IS_GAE or IS_CLOUD_RUN:
    # Cloud SQL via Unix Socket
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'monpec_db'),
            'USER': os.getenv('DB_USER', 'monpec_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': f'/cloudsql/{os.getenv("CLOUD_SQL_CONNECTION_NAME", "")}',
            'PORT': '',
        }
    }
else:
    # Cloud SQL via IP (Compute Engine ou local)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'monpec_db'),
            'USER': os.getenv('DB_USER', 'monpec_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

# Configurações de segurança
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Arquivos estáticos e mídia
# No Cloud Run/App Engine, usar Cloud Storage
USE_CLOUD_STORAGE = os.getenv('USE_CLOUD_STORAGE', 'False') == 'True'

if USE_CLOUD_STORAGE:
    # Usar Cloud Storage para arquivos estáticos e mídia
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStaticFilesStorage'
    GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME', 'monpec-static')
    GS_DEFAULT_ACL = 'publicRead'
else:
    # Usar sistema de arquivos local
    STATIC_URL = '/static/'
    STATIC_ROOT = '/app/staticfiles'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = '/app/media'
    
    # Adicionar WhiteNoise para servir arquivos estáticos
    # WhiteNoise já está no requirements_producao.txt
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Adicionar middleware para permitir hosts do Cloud Run dinamicamente
    MIDDLEWARE.insert(0, 'sistema_rural.middleware.CloudRunHostMiddleware')

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
            'propagate': True,
        },
        'gestao_rural': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# URLs do Stripe para produção
STRIPE_SUCCESS_URL = os.getenv('STRIPE_SUCCESS_URL', 'https://monpec.com.br/assinaturas/sucesso/')
STRIPE_CANCEL_URL = os.getenv('STRIPE_CANCEL_URL', 'https://monpec.com.br/assinaturas/cancelado/')

# Cache usando Cloud Memorystore (Redis) se disponível
REDIS_HOST = os.getenv('REDIS_HOST', '')
if REDIS_HOST:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f'redis://{REDIS_HOST}:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    # Cache em memória local
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Sessões
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

# Configurações específicas do Cloud Run
if IS_CLOUD_RUN:
    # Timeout para Cloud Run
    SECURE_SSL_REDIRECT = True
    USE_TZ = True

