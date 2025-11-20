# ========================================
# SISTEMA MONPEC COMPLETO - DESENVOLVIMENTO AUTOMÁTICO
# ========================================

Write-Host "🚀 INICIANDO DESENVOLVIMENTO DO SISTEMA MONPEC COMPLETO" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Yellow

# 1. CRIAR ESTRUTURA DO PROJETO
Write-Host "📁 Criando estrutura do projeto..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "monpec_local" -Force
Set-Location "monpec_local"

# Criar estrutura Django
New-Item -ItemType Directory -Path "monpec_sistema" -Force
New-Item -ItemType Directory -Path "gestao_rural" -Force
New-Item -ItemType Directory -Path "templates" -Force
New-Item -ItemType Directory -Path "templates/gestao_rural" -Force
New-Item -ItemType Directory -Path "static" -Force
New-Item -ItemType Directory -Path "static/css" -Force
New-Item -ItemType Directory -Path "static/js" -Force
New-Item -ItemType Directory -Path "media" -Force

Write-Host "✅ Estrutura criada!" -ForegroundColor Green

# 2. CRIAR ARQUIVOS DJANGO
Write-Host "⚙️ Criando arquivos Django..." -ForegroundColor Cyan

# manage.py
@"
#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monpec_sistema.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"@ | Out-File -FilePath "manage.py" -Encoding UTF8

# settings.py
@"
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-monpec-sistema-rural-2024'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gestao_rural',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'monpec_sistema.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'monpec_sistema.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações CSRF
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Configurações de login
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
"@ | Out-File -FilePath "monpec_sistema/settings.py" -Encoding UTF8

# urls.py principal
@"
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestao_rural.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"@ | Out-File -FilePath "monpec_sistema/urls.py" -Encoding UTF8

# wsgi.py
@"
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monpec_sistema.settings')
application = get_wsgi_application()
"@ | Out-File -FilePath "monpec_sistema/wsgi.py" -Encoding UTF8

# __init__.py
@"
"@ | Out-File -FilePath "monpec_sistema/__init__.py" -Encoding UTF8

Write-Host "✅ Arquivos Django criados!" -ForegroundColor Green

# 3. CRIAR APP GESTAO_RURAL
Write-Host "🏗️ Criando app gestao_rural..." -ForegroundColor Cyan

# __init__.py do app
@"
"@ | Out-File -FilePath "gestao_rural/__init__.py" -Encoding UTF8

# apps.py
@"
from django.apps import AppConfig

class GestaoRuralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestao_rural'
"@ | Out-File -FilePath "gestao_rural/apps.py" -Encoding UTF8

# models.py
@"
from django.db import models
from django.contrib.auth.models import User

class Proprietario(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Proprietário"
        verbose_name_plural = "Proprietários"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    @property
    def area_total(self):
        return sum(prop.area for prop in self.propriedades.all())

class Propriedade(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Propriedade")
    proprietario = models.ForeignKey(Proprietario, on_delete=models.CASCADE, related_name='propriedades', verbose_name="Proprietário")
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Área (hectares)")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    matricula = models.CharField(max_length=100, blank=True, null=True, verbose_name="Matrícula")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.proprietario.nome}"

class ProjetoCredito(models.Model):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('finalizado', 'Finalizado'),
    ]
    
    TIPO_CHOICES = [
        ('custeio', 'Custeio'),
        ('investimento', 'Investimento'),
        ('comercializacao', 'Comercialização'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='projetos', verbose_name="Propriedade")
    titulo = models.CharField(max_length=200, verbose_name="Título do Projeto")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Crédito")
    valor_solicitado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Solicitado (R$)")
    prazo_pagamento = models.IntegerField(verbose_name="Prazo (meses)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho', verbose_name="Status")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_vencimento = models.DateField(blank=True, null=True, verbose_name="Data de Vencimento")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Projeto de Crédito"
        verbose_name_plural = "Projetos de Crédito"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo} - {self.propriedade.nome}"

class Documento(models.Model):
    TIPO_CHOICES = [
        ('cpf', 'CPF'),
        ('rg', 'RG'),
        ('comprovante_renda', 'Comprovante de Renda'),
        ('matricula_imovel', 'Matrícula do Imóvel'),
        ('itbi', 'ITBI'),
        ('outros', 'Outros'),
    ]
    
    projeto = models.ForeignKey(ProjetoCredito, on_delete=models.CASCADE, related_name='documentos', verbose_name="Projeto")
    nome = models.CharField(max_length=200, verbose_name="Nome do Documento")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    arquivo = models.FileField(upload_to='documentos/', verbose_name="Arquivo")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.nome} - {self.projeto.titulo}"
"@ | Out-File -FilePath "gestao_rural/models.py" -Encoding UTF8

Write-Host "✅ App gestao_rural criado!" -ForegroundColor Green

Write-Host "🎉 SISTEMA MONPEC CRIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS:" -ForegroundColor Cyan
Write-Host "1. Execute: python manage.py makemigrations" -ForegroundColor White
Write-Host "2. Execute: python manage.py migrate" -ForegroundColor White
Write-Host "3. Execute: python manage.py createsuperuser" -ForegroundColor White
Write-Host "4. Execute: python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Acesse: http://127.0.0.1:8000" -ForegroundColor Green


