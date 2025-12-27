"""
Django settings for sistema_rural project - GOOGLE CLOUD PLATFORM

Configurações específicas para produção no Google Cloud Platform.
Suporta Cloud Run, App Engine e Compute Engine.
"""
import os

# CRÍTICO: Definir SECRET_KEY e DEBUG ANTES de importar settings para evitar ValueError
# Tentar obter de variável de ambiente primeiro
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    # Se não tiver, usar uma chave padrão (será sobrescrita depois se necessário)
    SECRET_KEY = '0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_$1ap4+4t'

# CRÍTICO: Definir DEBUG temporariamente como True para evitar ValueError no settings.py
# O settings.py valida SECRET_KEY e se DEBUG=False e SECRET_KEY=None, levanta ValueError
# Vamos definir DEBUG=True temporariamente, depois sobrescreveremos
DEBUG = os.getenv('DEBUG', 'False') == 'True'
if not SECRET_KEY or SECRET_KEY == 'YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE':
    # Se não tiver SECRET_KEY válida, garantir DEBUG=True temporariamente
    os.environ['DEBUG'] = 'True'

# Agora importar settings (que não vai dar erro porque SECRET_KEY está definida e DEBUG=True temporariamente)
from .settings import *

# Sobrescrever SECRET_KEY se estiver em variável de ambiente
env_secret_key = os.getenv('SECRET_KEY')
if env_secret_key:
    SECRET_KEY = env_secret_key

# Detectar se está rodando no Google Cloud
IS_GAE = os.getenv('GAE_ENV') is not None
IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None
# Cloud Run Jobs também podem ser detectados pela presença de CLOUD_SQL_CONNECTION_NAME
# ou pela variável GOOGLE_CLOUD_PROJECT (comum em ambos Cloud Run Service e Jobs)
IS_CLOUD_RUN_JOB = os.getenv('GOOGLE_CLOUD_PROJECT') is not None and os.getenv('K_SERVICE') is None
IS_CLOUD_RUN_ANY = IS_CLOUD_RUN or IS_CLOUD_RUN_JOB

# Configurações de produção (sobrescrever DEBUG que foi definido temporariamente)
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS para Google Cloud
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    'monpec-sistema-rural.uc.r.appspot.com',  # App Engine
    'monpec-29862706245.us-central1.run.app',  # Cloud Run - host específico
    'monpec-fzzfjppzva-uc.a.run.app',  # Cloud Run - host alternativo
    'localhost',
    '127.0.0.1',
    '*',  # Permitir todos os hosts do Cloud Run (será filtrado pelo middleware)
]

# Adicionar hosts do Cloud Run
# Cloud Run URLs têm formato: SERVICE-PROJECT_HASH-REGION.a.run.app
if IS_CLOUD_RUN_ANY:
    # Obter host do Cloud Run via variável de ambiente
    cloud_run_host = os.getenv('CLOUD_RUN_HOST', '')
    if cloud_run_host:
        ALLOWED_HOSTS.append(cloud_run_host)
    
    # Tentar construir o host padrão do Cloud Run
    # Formatos possíveis: 
    # - SERVICE-PROJECT_ID.REGION.run.app
    # - SERVICE-PROJECT_ID.REGION.a.run.app
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', os.getenv('GCP_PROJECT', ''))
    service_name = os.getenv('K_SERVICE', 'monpec')
    region = os.getenv('REGION', 'us-central1')
    
    if project_id and service_name:
        # Adicionar ambos os formatos possíveis do Cloud Run
        default_cloud_run_host1 = f'{service_name}-{project_id}.{region}.run.app'
        default_cloud_run_host2 = f'{service_name}-{project_id}.{region}.a.run.app'
        
        if default_cloud_run_host1 not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(default_cloud_run_host1)
        if default_cloud_run_host2 not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(default_cloud_run_host2)

# Configuração CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://monpec.com.br',
    'https://www.monpec.com.br',
    'http://monpec.com.br',  # HTTP também (caso não tenha SSL configurado)
    'http://www.monpec.com.br',  # HTTP também (caso não tenha SSL configurado)
    'https://monpec-sistema-rural.uc.r.appspot.com',
]

# Adicionar origem do Cloud Run
if IS_CLOUD_RUN_ANY:
    cloud_run_host = os.getenv('CLOUD_RUN_HOST', '')
    if cloud_run_host:
        CSRF_TRUSTED_ORIGINS.append(f'https://{cloud_run_host}')
    
    # Adicionar URL padrão do Cloud Run se disponível
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', os.getenv('GCP_PROJECT', ''))
    service_name = os.getenv('K_SERVICE', 'monpec')
    region = os.getenv('REGION', 'us-central1')
    
    if project_id and service_name:
        # Adicionar ambos os formatos possíveis do Cloud Run
        default_cloud_run_url1 = f'https://{service_name}-{project_id}.{region}.run.app'
        default_cloud_run_url2 = f'https://{service_name}-{project_id}.{region}.a.run.app'
        
        if default_cloud_run_url1 not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(default_cloud_run_url1)
        if default_cloud_run_url2 not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(default_cloud_run_url2)

# Banco de dados - Cloud SQL via Unix Socket (App Engine/Cloud Run/Cloud Run Jobs)
CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME', '').strip()
DB_NAME = os.getenv('DB_NAME', 'monpec_db')
DB_USER = os.getenv('DB_USER', 'monpec_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

# Se estiver no Google Cloud (App Engine ou Cloud Run), usar Unix Socket
if IS_GAE or IS_CLOUD_RUN_ANY:
    # Se CLOUD_SQL_CONNECTION_NAME não estiver definido, usar valor padrão
    if not CLOUD_SQL_CONNECTION_NAME:
        CLOUD_SQL_CONNECTION_NAME = 'monpec-sistema-rural:us-central1:monpec-db'
        import warnings
        warnings.warn(
            f'CLOUD_SQL_CONNECTION_NAME não definido via variável de ambiente. Usando padrão: {CLOUD_SQL_CONNECTION_NAME}',
            UserWarning
        )
    
    # Sempre usar Unix Socket no Google Cloud
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': f'/cloudsql/{CLOUD_SQL_CONNECTION_NAME}',
            'PORT': '',
        }
    }
elif CLOUD_SQL_CONNECTION_NAME:
    # Se CLOUD_SQL_CONNECTION_NAME estiver definido mas não estiver no Cloud, usar socket também
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': f'/cloudsql/{CLOUD_SQL_CONNECTION_NAME}',
            'PORT': '',
        }
    }
else:
    # Cloud SQL via IP (Compute Engine ou local)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
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
    # STATICFILES_DIRS já está herdado de settings.py via 'from .settings import *'
    # Ele aponta para BASE_DIR / 'static' onde estão os arquivos originais (vídeos, imagens, etc.)
    # O collectstatic copia esses arquivos para STATIC_ROOT (/app/staticfiles)
    # O WhiteNoise então serve os arquivos de STATIC_ROOT automaticamente
    MEDIA_URL = '/media/'
    MEDIA_ROOT = '/app/media'
    
    # Adicionar WhiteNoise para servir arquivos estáticos
    # Verificar se whitenoise está disponível antes de adicionar
    try:
        import whitenoise
        # Adicionar WhiteNoise após SecurityMiddleware
        if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
            try:
                security_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
                MIDDLEWARE.insert(security_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
            except (ValueError, AttributeError):
                # Se não encontrar, adicionar no início
                if isinstance(MIDDLEWARE, list):
                    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
        
        # Usar CompressedStaticFilesStorage
        STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    except ImportError:
        # Se whitenoise não estiver instalado, usar configuração padrão
        pass
    
    # Adicionar middleware para permitir hosts do Cloud Run dinamicamente
    # Verificar se o middleware existe antes de adicionar
    try:
        from sistema_rural.middleware import CloudRunHostMiddleware
        if 'sistema_rural.middleware.CloudRunHostMiddleware' not in MIDDLEWARE:
            if isinstance(MIDDLEWARE, list):
                MIDDLEWARE.insert(0, 'sistema_rural.middleware.CloudRunHostMiddleware')
    except (ImportError, AttributeError):
        # Se o middleware não existir, continuar sem ele
        pass

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

# Configurações do Mercado Pago para produção
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
MERCADOPAGO_PUBLIC_KEY = os.getenv('MERCADOPAGO_PUBLIC_KEY', '')
MERCADOPAGO_WEBHOOK_SECRET = os.getenv('MERCADOPAGO_WEBHOOK_SECRET', '')
MERCADOPAGO_SUCCESS_URL = os.getenv('MERCADOPAGO_SUCCESS_URL', 'https://monpec.com.br/assinaturas/sucesso/')
MERCADOPAGO_CANCEL_URL = os.getenv('MERCADOPAGO_CANCEL_URL', 'https://monpec.com.br/assinaturas/cancelado/')
PAYMENT_GATEWAY_DEFAULT = os.getenv('PAYMENT_GATEWAY_DEFAULT', 'mercadopago')
SITE_URL = os.getenv('SITE_URL', 'https://monpec.com.br')

# Google Analytics (pode ser sobrescrito via variável de ambiente)
# Prioridade: variável de ambiente > settings.py (já importado via 'from .settings import *')
# Usar getattr para acessar o valor já importado de settings.py de forma segura
_current_ga_id = globals().get('GOOGLE_ANALYTICS_ID', '')
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', _current_ga_id)

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
if IS_CLOUD_RUN_ANY:
    # Timeout para Cloud Run
    SECURE_SSL_REDIRECT = True
    USE_TZ = True

