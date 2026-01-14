"""
Django settings for MONPEC - GOOGLE CLOUD DEPLOY OTIMIZADO
Configurações específicas para produção no Google Cloud Platform
Resolve problemas de migrações, PDF/Excel e linha 22
"""

import os
from pathlib import Path
from .settings import *

# =============================================================================
# CONFIGURAÇÕES DO GOOGLE CLOUD
# =============================================================================

# Detectar ambiente do Google Cloud
IS_GAE = os.getenv('GAE_ENV') is not None
IS_CLOUD_RUN = os.getenv('K_SERVICE') is not None or os.getenv('CLOUD_RUN_JOB') is not None

# Forçar detecção do Cloud Run se GOOGLE_CLOUD_PROJECT estiver definido
if not IS_CLOUD_RUN and os.getenv('GOOGLE_CLOUD_PROJECT'):
    IS_CLOUD_RUN = True

# =============================================================================
# CONFIGURAÇÕES DE PRODUÇÃO
# =============================================================================

DEBUG = False  # Sempre False em produção

# SECRET_KEY garantida para produção
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-production-key-monpec-2025-final-fixed')
print(f"DEBUG: SECRET_KEY configurada: {SECRET_KEY[:20]}...")  # Log para confirmar

# ALLOWED_HOSTS otimizado para GCP
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    'monpec-sistema-rural.uc.r.appspot.com',
    'monpec-29862706245.us-central1.run.app',
    'monpec-fzzfjppzva-uc.a.run.app',
    'monpec-app-fzzfjppzva-uc.a.run.app',  # Host específico do erro atual
    'monpec-app-29862706245.us-central1.run.app',  # Host atual do serviço
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    # Wildcards para Cloud Run
    '*.run.app',
    '*.a.run.app',
    '*.uc.a.run.app',
    '*.us-central1.run.app',
]

# Adicionar hosts dinâmicos do Cloud Run
if IS_CLOUD_RUN:
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', os.getenv('GCP_PROJECT', ''))
    service_name = os.getenv('K_SERVICE', 'monpec')
    region = os.getenv('REGION', 'us-central1')

    if project_id and service_name:
        cloud_run_hosts = [
            f'{service_name}-{project_id}.{region}.run.app',
            f'{service_name}-{project_id}.{region}.a.run.app',
            f'{service_name}-{project_id}.us-central1.run.app',
            f'{service_name}-{project_id}.us-central1.a.run.app',
        ]
        ALLOWED_HOSTS.extend(cloud_run_hosts)

# =============================================================================
# BANCO DE DADOS - POSTGRESQL OBRIGATÓRIO
# =============================================================================

# Verificar se estamos em ambiente de CI/CD (GitHub Actions)
IS_CI_CD = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

if IS_CI_CD:
    # Usar SQLite para testes no CI/CD (não requer servidor PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # Banco em memória para testes
        }
    }
else:
    # Configuração PostgreSQL para produção no Cloud Run
    if IS_CLOUD_RUN:
        # Cloud Run usa socket Unix para Cloud SQL
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'monpec-db',
                'USER': 'postgres',
                'PASSWORD': 'L6171r12@@jjms',
                'HOST': '/cloudsql/monpec-sistema-rural:us-central1:monpec-db',
                'PORT': '',  # Vazio para socket Unix
                'OPTIONS': {
                    'sslmode': 'disable',  # Cloud SQL gerencia SSL
                },
                'CONN_MAX_AGE': 60,
                'ATOMIC_REQUESTS': True,
            }
        }
    else:
        # Configuração para desenvolvimento local (se necessário)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME', 'monpec-db'),
                'USER': os.getenv('DB_USER', 'postgres'),
                'PASSWORD': os.getenv('DB_PASSWORD', 'L6171r12@@jjms'),
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', '5432'),
                'OPTIONS': {
                    'sslmode': 'prefer',
                },
                'CONN_MAX_AGE': 60,
                'ATOMIC_REQUESTS': True,
            }
        }

# =============================================================================
# ARQUIVOS ESTÁTICOS E MÍDIA - GOOGLE CLOUD STORAGE
# =============================================================================

# Configuração do Google Cloud Storage para arquivos estáticos
GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME', 'monpec-static-files')
GS_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', '')

if GS_PROJECT_ID and GS_BUCKET_NAME:
    from google.oauth2 import service_account
    import json

    GS_CREDENTIALS = None
    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
    if credentials_json:
        try:
            GS_CREDENTIALS = service_account.Credentials.from_service_account_info(
                json.loads(credentials_json)
            )
        except:
            pass

    # Configuração do Cloud Storage
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_DEFAULT_ACL = 'publicRead'

    # Arquivos estáticos
    STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME_STATIC = GS_BUCKET_NAME

# Diretórios de arquivos
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# CONFIGURAÇÕES DE EMAIL - GMAIL COM APP PASSWORD
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'l.moncaosilva@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')  # App Password obrigatório
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'l.moncaosilva@gmail.com')

# =============================================================================
# CONFIGURAÇÕES DE SEGURANÇA PARA GCP
# =============================================================================

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

if IS_CLOUD_RUN or IS_GAE:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# =============================================================================
# CONFIGURAÇÕES DE CACHE E PERFORMANCE
# =============================================================================

# Redis para cache (se disponível)
REDIS_URL = os.getenv('REDIS_URL')
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

# =============================================================================
# LOGGING PARA GCP
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'gcp_formatter': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'gcp_formatter',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'gestao_rural': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# CONFIGURAÇÕES ESPECÍFICAS DO MONPEC PARA GCP
# =============================================================================

# URL do site
SITE_URL = os.getenv('SITE_URL', 'https://monpec.com.br')

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
MERCADOPAGO_PUBLIC_KEY = os.getenv('MERCADOPAGO_PUBLIC_KEY', '')

# Consultor
CONSULTOR_EMAIL = os.getenv('CONSULTOR_EMAIL', 'l.moncaosilva@gmail.com')
CONSULTOR_TELEFONE = os.getenv('CONSULTOR_TELEFONE', '67999688561')  # WhatsApp configurado

# =============================================================================
# MIDDLEWARE OTIMIZADO PARA GCP
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middleware do Monpec
    'gestao_rural.middleware_liberacao_acesso.LiberacaoAcessoMiddleware',
]

# =============================================================================
# APPS ADICIONAIS PARA GCP
# =============================================================================

INSTALLED_APPS = list(INSTALLED_APPS)  # Copiar da settings base

# Adicionar apps específicos do GCP
if GS_PROJECT_ID:
    INSTALLED_APPS.append('storages')

# =============================================================================
# CONFIGURAÇÕES DE PDF E EXCEL (CORREÇÃO DOS ERROS)
# =============================================================================

# ReportLab para PDF
try:
    import reportlab
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# OpenPyXL para Excel
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# WeasyPrint como alternativa (import sob demanda)
WEASYPRINT_AVAILABLE = False  # Será verificado quando necessário

# Configurações de exportação
EXPORT_CONFIG = {
    'PDF_ENGINE': 'reportlab' if REPORTLAB_AVAILABLE else ('weasyprint' if WEASYPRINT_AVAILABLE else 'fallback'),
    'EXCEL_ENGINE': 'openpyxl' if OPENPYXL_AVAILABLE else 'fallback',
    'TEMP_DIR': '/tmp' if IS_CLOUD_RUN else BASE_DIR / 'temp',
}

# Criar diretório temp se não existir
temp_dir = Path(EXPORT_CONFIG['TEMP_DIR'])
temp_dir.mkdir(parents=True, exist_ok=True)

print(f"🚀 MONPEC GCP DEPLOY CONFIGURADO")
print(f"📍 Ambiente: {'Cloud Run' if IS_CLOUD_RUN else 'App Engine' if IS_GAE else 'Desenvolvimento'}")
print(f"🗄️ Banco: PostgreSQL")
print(f"📧 Email: {EMAIL_HOST_USER}")
print(f"📊 PDF: {EXPORT_CONFIG['PDF_ENGINE']}")
print(f"📈 Excel: {EXPORT_CONFIG['EXCEL_ENGINE']}")