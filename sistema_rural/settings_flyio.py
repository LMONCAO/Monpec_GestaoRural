"""
Django settings for sistema_rural project - FLY.IO

Configurações específicas para produção no Fly.io.
"""
import os
from urllib.parse import urlparse

# IMPORTANTE: Configurar DATABASE_URL ANTES de importar settings.py
# para evitar que o settings.py base configure SQLite
DATABASE_URL = os.getenv('DATABASE_URL', '')

from .settings import *

# Detectar se está rodando no Fly.io
IS_FLY_IO = os.getenv('FLY_APP_NAME') is not None

# Configurações de produção
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS para Fly.io
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    'localhost',
    '127.0.0.1',
]

# Adicionar host do Fly.io dinamicamente
if IS_FLY_IO:
    fly_app_name = os.getenv('FLY_APP_NAME', 'monpec-gestaorural')
    fly_region = os.getenv('FLY_REGION', 'gru')
    # Fly.io usa formato: app-name.fly.dev
    fly_host = f'{fly_app_name}.fly.dev'
    ALLOWED_HOSTS.append(fly_host)
    
    # IMPORTANTE: IPs internos do Fly.io (172.x.x.x) serão permitidos
    # dinamicamente pelo FlyIOHostMiddleware para health checks.
    # Não precisamos adicionar IPs específicos aqui.

# Configuração CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://monpec.com.br',
    'https://www.monpec.com.br',
]

# Adicionar origem do Fly.io
if IS_FLY_IO:
    fly_app_name = os.getenv('FLY_APP_NAME', 'monpec-gestaorural')
    fly_host = f'https://{fly_app_name}.fly.dev'
    CSRF_TRUSTED_ORIGINS.append(fly_host)

# Banco de dados - Fly.io usa DATABASE_URL
import logging
logger = logging.getLogger(__name__)

# Fly.io fornece DATABASE_URL no formato: postgres://user:password@host:port/dbname
# DATABASE_URL já foi obtido no início do arquivo, mas vamos garantir
if not DATABASE_URL:
    DATABASE_URL = os.getenv('DATABASE_URL', '')

if DATABASE_URL:
    # Parse da URL do banco de dados
    try:
        parsed = urlparse(DATABASE_URL)
        DB_NAME = parsed.path[1:]  # Remove a barra inicial
        DB_USER = parsed.username
        DB_PASSWORD = parsed.password
        DB_HOST = parsed.hostname
        DB_PORT = parsed.port or '5432'
        
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
                    'options': '-c statement_timeout=300000',  # 5 minutos
                },
                'CONN_MAX_AGE': 600,  # Reutilizar conexões por até 10 minutos
            }
        }
        logger.info(f"✅ Banco de dados configurado via DATABASE_URL: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    except Exception as e:
        logger.error(f"❌ Erro ao parsear DATABASE_URL: {e}")
        raise
else:
    # Fallback: usar variáveis individuais (compatibilidade)
    DB_NAME = os.getenv('DB_NAME', 'monpec_db')
    DB_USER = os.getenv('DB_USER', 'monpec_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
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
    logger.warning(f"⚠️ DATABASE_URL não definido, usando variáveis individuais: {DB_HOST}:{DB_PORT}/{DB_NAME}")

# Validação final
if not DATABASES['default']['NAME']:
    raise ValueError("Nome do banco de dados não está definido!")
if not DATABASES['default']['USER']:
    raise ValueError("Usuário do banco de dados não está definido!")

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
# Fly.io usa sistema de arquivos local (com volumes se necessário)
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media'

# Criar diretórios se não existirem
import os
os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)

logger.info(f'✅ Sistema de arquivos configurado: MEDIA_ROOT={MEDIA_ROOT}, STATIC_ROOT={STATIC_ROOT}')

# Adicionar middleware para permitir IPs internos do Fly.io
# Este middleware DEVE ser o primeiro para interceptar antes da validação padrão
try:
    from sistema_rural.middleware import FlyIOHostMiddleware
    middleware_path = 'sistema_rural.middleware.FlyIOHostMiddleware'
    if middleware_path not in MIDDLEWARE:
        if isinstance(MIDDLEWARE, list):
            # Inserir no início da lista (antes de qualquer outro middleware)
            MIDDLEWARE.insert(0, middleware_path)
            logger.info('✅ FlyIOHostMiddleware adicionado para permitir IPs internos')
except (ImportError, AttributeError) as e:
    logger.warning(f"⚠️ Não foi possível adicionar FlyIOHostMiddleware: {e}")

# Adicionar WhiteNoise para servir arquivos estáticos
if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    try:
        security_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
        MIDDLEWARE.insert(security_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    except (ValueError, AttributeError):
        if isinstance(MIDDLEWARE, list):
            MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Configurações do WhiteNoise
WHITENOISE_USE_FINDERS = False
WHITENOISE_AUTOREFRESH = False
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ROOT = STATIC_ROOT
WHITENOISE_MAX_AGE = 31536000

WHITENOISE_MIMETYPES = {
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
}

logger.info(f'✅ WhiteNoise configurado para servir arquivos de: {STATIC_ROOT}')

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

# Google Analytics
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', GOOGLE_ANALYTICS_ID if 'GOOGLE_ANALYTICS_ID' in globals() else '')

# Cache em memória local (Fly.io não tem Redis por padrão, mas pode ser adicionado)
REDIS_URL = os.getenv('REDIS_URL', '')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
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

# Handler customizado para erro 500
handler500 = 'gestao_rural.views_errors.handler500'

# Configurações específicas do Fly.io
USE_TZ = True
