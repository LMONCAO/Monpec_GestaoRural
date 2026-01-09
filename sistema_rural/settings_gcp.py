"""
Django settings for sistema_rural project - GOOGLE CLOUD PLATFORM

Configurações específicas para produção no Google Cloud Platform.
Suporta Cloud Run, App Engine e Compute Engine.
"""
import os
from .settings import *

# Detectar se está rodando no Google Cloud
IS_GAE = os.getenv('GAE_ENV') is not None
IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None or os.getenv('CLOUD_RUN_JOB') is not None

# Forçar detecção do Cloud Run (temporário para debug)
if not IS_CLOUD_RUN and os.getenv('GOOGLE_CLOUD_PROJECT'):
    IS_CLOUD_RUN = True

# Configurações de produção
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS para Google Cloud
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    'monpec-sistema-rural.uc.r.appspot.com',  # App Engine
    'monpec-29862706245.us-central1.run.app',  # Cloud Run - host específico
    'monpec-fzzfjppzva-uc.a.run.app',  # Domínio específico do Cloud Run
    'localhost',
    '127.0.0.1',
]

# Adicionar hosts do Cloud Run dinamicamente
# Cloud Run URLs têm formato: SERVICE-PROJECT_HASH-REGION.a.run.app
if IS_CLOUD_RUN:
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
    
    # Em produção no Cloud Run, permitir qualquer host do Cloud Run
    # O middleware CloudRunHostMiddleware vai adicionar dinamicamente se necessário

# Configuração CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://monpec.com.br',
    'https://www.monpec.com.br',
    'https://monpec-sistema-rural.uc.r.appspot.com',
    'https://monpec-fzzfjppzva-uc.a.run.app',  # Domínio específico do Cloud Run
]

# Adicionar origem do Cloud Run
if IS_CLOUD_RUN:
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
    
    # O middleware CloudRunHostMiddleware vai adicionar dinamicamente
    # as origens do Cloud Run conforme necessário

# Banco de dados - Cloud SQL via Unix Socket (App Engine/Cloud Run/Cloud Run Jobs)
import logging
logger = logging.getLogger(__name__)

CLOUD_SQL_CONNECTION_NAME = os.getenv('CLOUD_SQL_CONNECTION_NAME', '')
DB_NAME = os.getenv('DB_NAME', 'monpec_db')
DB_USER = os.getenv('DB_USER', 'monpec_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '')
DB_PORT = os.getenv('DB_PORT', '5432')

# Log de diagnóstico (sem expor senha)
logger.info(f"🔍 Diagnóstico de Banco de Dados:")
logger.info(f"   IS_GAE: {IS_GAE}")
logger.info(f"   IS_CLOUD_RUN: {IS_CLOUD_RUN}")
logger.info(f"   CLOUD_SQL_CONNECTION_NAME: {CLOUD_SQL_CONNECTION_NAME[:50] if CLOUD_SQL_CONNECTION_NAME else 'NÃO DEFINIDO'}")
logger.info(f"   DB_NAME: {DB_NAME}")
logger.info(f"   DB_USER: {DB_USER}")
logger.info(f"   DB_PASSWORD: {'DEFINIDO' if DB_PASSWORD else 'NÃO DEFINIDO'}")
logger.info(f"   DB_HOST: {DB_HOST if DB_HOST else 'NÃO DEFINIDO (usando Unix Socket)'}")

# Configurar banco de dados
if IS_GAE or IS_CLOUD_RUN or CLOUD_SQL_CONNECTION_NAME:
    # TEMPORARIAMENTE FORÇANDO TCP/IP por causa de problemas com socket Unix nos jobs
    # Cloud SQL via TCP/IP (fallback para quando socket não funciona)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST or '34.9.51.178',  # IP público do Cloud SQL
            'PORT': DB_PORT or '5432',
            'OPTIONS': {
                'connect_timeout': 30,
                'options': '-c statement_timeout=300000',  # 5 minutos (300 segundos) - aumentado para migrações complexas
            },
            'CONN_MAX_AGE': 600,  # Reutilizar conexões por até 10 minutos
        }
    }
    logger.info(f"✅ Configurado: Cloud SQL via TCP/IP: {DB_HOST or '34.9.51.178'}:{DB_PORT or '5432'}")
else:
    # Cloud SQL via IP (Compute Engine ou desenvolvimento local)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST if DB_HOST else '127.0.0.1',
            'PORT': DB_PORT,
            'OPTIONS': {
                'connect_timeout': 10,
            },
            'CONN_MAX_AGE': 600,
        }
    }
    logger.info(f"✅ Configurado: Conexão TCP/IP para {DB_HOST if DB_HOST else '127.0.0.1'}:{DB_PORT}")

# Validação final: verificar se todas as variáveis necessárias estão definidas
if not DB_NAME:
    raise ValueError("DB_NAME não está definido!")
if not DB_USER:
    raise ValueError("DB_USER não está definido!")
if not DB_PASSWORD:
    logger.warning("⚠️ DB_PASSWORD não está definido! A conexão pode falhar.")

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

# MEDIA_URL sempre deve estar configurado (mesmo com Cloud Storage)
# Isso é necessário para que {{ object.foto.url }} funcione nos templates
MEDIA_URL = '/media/'

if USE_CLOUD_STORAGE:
    # Usar Cloud Storage para arquivos estáticos e mídia
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStaticFilesStorage'
    GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME', 'monpec-static')
    GS_DEFAULT_ACL = 'publicRead'
    
    # Configurações adicionais do Cloud Storage
    GS_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', os.getenv('GCP_PROJECT', ''))
    GS_LOCATION = ''  # Raiz do bucket
    
    # IMPORTANTE: Com Cloud Storage, os arquivos são salvos diretamente no bucket
    # A URL será gerada automaticamente pelo django-storages
    # Mas ainda precisamos do MEDIA_URL para que o Django saiba como construir as URLs
    logger.info(f'✅ Cloud Storage configurado: bucket={GS_BUCKET_NAME}, project={GS_PROJECT_ID}')
else:
    # Usar sistema de arquivos local
    STATIC_URL = '/static/'
    STATIC_ROOT = '/app/staticfiles'
    # STATICFILES_DIRS já está herdado de settings.py via 'from .settings import *'
    # Ele aponta para BASE_DIR / 'static' onde estão os arquivos originais (vídeos, imagens, etc.)
    # O collectstatic copia esses arquivos para STATIC_ROOT (/app/staticfiles)
    # O WhiteNoise então serve os arquivos de STATIC_ROOT automaticamente
    # MEDIA_URL já foi definido acima
    MEDIA_ROOT = '/app/media'
    
    # Criar diretório de mídia se não existir
    import os
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    logger.info(f'✅ Sistema de arquivos local configurado: MEDIA_ROOT={MEDIA_ROOT}, MEDIA_URL={MEDIA_URL}')
    
    # Adicionar WhiteNoise para servir arquivos estáticos
    # WhiteNoise já está no requirements_producao.txt
    if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
        try:
            security_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
            MIDDLEWARE.insert(security_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
        except (ValueError, AttributeError):
            # Se não encontrar SecurityMiddleware, adicionar no início
            if isinstance(MIDDLEWARE, list):
                MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    
    # Usar CompressedStaticFilesStorage em vez de CompressedManifestStaticFilesStorage
    # para evitar erros de manifest missing em produção
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    
    # Configurações adicionais do WhiteNoise
    # WhiteNoise serve arquivos de STATIC_ROOT automaticamente
    # Isso inclui vídeos (.mp4), imagens (.jpeg, .png), ícones e outros arquivos estáticos coletados pelo collectstatic
    # WhiteNoise por padrão serve arquivos até 2GB, o que é suficiente para vídeos
    
    # Configurações do WhiteNoise para garantir que imagens sejam servidas corretamente
    # IMPORTANTE: WhiteNoise serve arquivos de STATIC_ROOT, não de STATICFILES_DIRS
    # Por isso, os arquivos DEVEM ser coletados com collectstatic antes
    WHITENOISE_USE_FINDERS = False  # Desabilitado: usar apenas STATIC_ROOT (mais rápido e confiável)
    WHITENOISE_AUTOREFRESH = False  # Desabilitado em produção (arquivos já foram coletados)
    WHITENOISE_MANIFEST_STRICT = False  # Não falha se arquivo não estiver no manifest
    WHITENOISE_ROOT = STATIC_ROOT  # Diretório raiz dos arquivos estáticos (/app/staticfiles)
    
    # Garantir que imagens JPEG sejam servidas corretamente
    # Adicionar mais tipos MIME para garantir que todas as imagens sejam servidas
    # IMPORTANTE: Isso é crítico para as fotos do slideshow (foto1.jpeg a foto6.jpeg)
    WHITENOISE_MIMETYPES = {
        '.jpeg': 'image/jpeg',
        '.jpg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
    }
    
    # Log para verificar se as fotos estão sendo servidas
    logger.info(f'✅ WhiteNoise configurado para servir arquivos de: {STATIC_ROOT}')
    logger.info(f'✅ Tipos MIME configurados para imagens JPEG, PNG, etc.')
    
    # Configurar WhiteNoise para servir arquivos com cache apropriado
    # Imagens devem ter cache longo, mas permitir revalidação
    WHITENOISE_MAX_AGE = 31536000  # 1 ano (padrão)
    
    # Adicionar headers CORS se necessário (para imagens)
    WHITENOISE_ADD_HEADERS_FUNCTION = None  # Usar padrão do WhiteNoise
    
    # IMPORTANTE: Media files serão servidos via view customizada no urls.py
    # O WhiteNoise serve apenas static files, então media files precisam de tratamento especial
    
    # Adicionar middleware para permitir hosts do Cloud Run dinamicamente
    # Verificar se o middleware existe antes de adicionar
    try:
        from sistema_rural.middleware import CloudRunHostMiddleware
        middleware_path = 'sistema_rural.middleware.CloudRunHostMiddleware'
        if middleware_path not in MIDDLEWARE:
            if isinstance(MIDDLEWARE, list):
                # Tentar inserir ANTES do CommonMiddleware
                try:
                    common_index = MIDDLEWARE.index('django.middleware.common.CommonMiddleware')
                    MIDDLEWARE.insert(common_index, middleware_path)
                except ValueError:
                    # Se não encontrar CommonMiddleware, inserir no início
                    MIDDLEWARE.insert(0, middleware_path)
    except (ImportError, AttributeError) as e:
        # Se o middleware não existir, apenas logar aviso (não quebrar)
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Não foi possível adicionar CloudRunHostMiddleware: {e}")
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

# Google Analytics (pode ser sobrescrito via variável de ambiente)
# Prioridade: variável de ambiente > settings.py
GOOGLE_ANALYTICS_ID = os.getenv('GOOGLE_ANALYTICS_ID', GOOGLE_ANALYTICS_ID if 'GOOGLE_ANALYTICS_ID' in globals() else '')

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

# Handler customizado para erro 500 - redireciona para dashboard
handler500 = 'gestao_rural.views_errors.handler500'

# Configurações específicas do Cloud Run
if IS_CLOUD_RUN:
    # Timeout para Cloud Run
    SECURE_SSL_REDIRECT = True
    USE_TZ = True

