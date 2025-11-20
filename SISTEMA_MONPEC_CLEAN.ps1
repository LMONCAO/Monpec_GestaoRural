# ========================================
# SISTEMA MONPEC CLEAN - DESIGN MODERNO
# ========================================

Write-Host "🎨 CRIANDO SISTEMA MONPEC COM DESIGN CLEAN" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Yellow

# 1. CRIAR ESTRUTURA
Write-Host "📁 Criando estrutura do projeto..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path "monpec_clean" -Force
Set-Location "monpec_clean"

# Criar estrutura Django
New-Item -ItemType Directory -Path "monpec_sistema" -Force
New-Item -ItemType Directory -Path "gestao_rural" -Force
New-Item -ItemType Directory -Path "templates" -Force
New-Item -ItemType Directory -Path "templates/gestao_rural" -Force
New-Item -ItemType Directory -Path "static" -Force
New-Item -ItemType Directory -Path "static/css" -Force
New-Item -ItemType Directory -Path "static/js" -Force
New-Item -ItemType Directory -Path "media" -Force

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

CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

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
"@ | Out-File -FilePath "gestao_rural/models.py" -Encoding UTF8

# views.py
@"
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from .models import Proprietario, Propriedade, ProjetoCredito
import json
from datetime import datetime, date
import csv

def landing_page(request):
    return render(request, 'gestao_rural/landing.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos')
    return render(request, 'gestao_rural/login.html')

def logout_view(request):
    logout(request)
    return redirect('landing_page')

@login_required
def dashboard(request):
    total_proprietarios = Proprietario.objects.count()
    total_propriedades = Propriedade.objects.count()
    total_projetos = ProjetoCredito.objects.count()
    projetos_aprovados = ProjetoCredito.objects.filter(status='aprovado').count()
    
    projetos_recentes = ProjetoCredito.objects.select_related('propriedade__proprietario').order_by('-created_at')[:5]
    proprietarios_recentes = Proprietario.objects.order_by('-created_at')[:5]
    
    context = {
        'total_proprietarios': total_proprietarios,
        'total_propriedades': total_propriedades,
        'total_projetos': total_projetos,
        'projetos_aprovados': projetos_aprovados,
        'projetos_recentes': projetos_recentes,
        'proprietarios_recentes': proprietarios_recentes,
    }
    return render(request, 'gestao_rural/dashboard.html', context)

@login_required
def proprietarios_lista(request):
    search = request.GET.get('search', '')
    proprietarios = Proprietario.objects.all()
    
    if search:
        proprietarios = proprietarios.filter(
            Q(nome__icontains=search) | 
            Q(cpf__icontains=search) | 
            Q(cidade__icontains=search)
        )
    
    paginator = Paginator(proprietarios, 10)
    page_number = request.GET.get('page')
    proprietarios = paginator.get_page(page_number)
    
    return render(request, 'gestao_rural/proprietarios_lista.html', {
        'proprietarios': proprietarios,
        'search': search
    })

@login_required
def proprietario_novo(request):
    if request.method == 'POST':
        try:
            nome = request.POST.get('nome')
            cpf = request.POST.get('cpf')
            telefone = request.POST.get('telefone', '')
            email = request.POST.get('email', '')
            endereco = request.POST.get('endereco', '')
            cidade = request.POST.get('cidade', '')
            estado = request.POST.get('estado', '')
            observacoes = request.POST.get('observacoes', '')
            
            if not nome or not cpf:
                messages.error(request, 'Nome e CPF são obrigatórios!')
                return render(request, 'gestao_rural/proprietario_novo.html')
            
            if Proprietario.objects.filter(cpf=cpf).exists():
                messages.error(request, 'CPF já cadastrado!')
                return render(request, 'gestao_rural/proprietario_novo.html')
            
            proprietario = Proprietario.objects.create(
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                endereco=endereco,
                cidade=cidade,
                estado=estado,
                observacoes=observacoes
            )
            
            messages.success(request, f'Proprietário {nome} cadastrado com sucesso!')
            return redirect('proprietarios_lista')
            
        except Exception as e:
            messages.error(request, f'Erro ao cadastrar: {str(e)}')
    
    return render(request, 'gestao_rural/proprietario_novo.html')

@login_required
def propriedades_lista(request):
    search = request.GET.get('search', '')
    proprietario_id = request.GET.get('proprietario', '')
    
    propriedades = Propriedade.objects.select_related('proprietario')
    
    if search:
        propriedades = propriedades.filter(
            Q(nome__icontains=search) | 
            Q(proprietario__nome__icontains=search) |
            Q(municipio__icontains=search)
        )
    
    if proprietario_id:
        propriedades = propriedades.filter(proprietario_id=proprietario_id)
    
    paginator = Paginator(propriedades, 10)
    page_number = request.GET.get('page')
    propriedades = paginator.get_page(page_number)
    
    proprietarios = Proprietario.objects.all()
    
    return render(request, 'gestao_rural/propriedades_lista.html', {
        'propriedades': propriedades,
        'proprietarios': proprietarios,
        'search': search,
        'proprietario_id': proprietario_id
    })

@login_required
def propriedade_modulos(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/propriedade_modulos.html', {'propriedade': propriedade})

@login_required
def pecuaria_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/pecuaria_dashboard.html', {'propriedade': propriedade})

@login_required
def agricultura_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/agricultura_dashboard.html', {'propriedade': propriedade})

@login_required
def financeiro_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/financeiro_dashboard.html', {'propriedade': propriedade})

@login_required
def patrimonio_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/patrimonio_dashboard.html', {'propriedade': propriedade})

@login_required
def projetos_dashboard(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    projetos = propriedade.projetos.all()
    return render(request, 'gestao_rural/projetos_dashboard.html', {
        'propriedade': propriedade,
        'projetos': projetos
    })

@login_required
def relatorio_final(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    return render(request, 'gestao_rural/relatorio_final.html', {'propriedade': propriedade})
"@ | Out-File -FilePath "gestao_rural/views.py" -Encoding UTF8

# urls.py do app
@"
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proprietarios/', views.proprietarios_lista, name='proprietarios_lista'),
    path('proprietarios/novo/', views.proprietario_novo, name='proprietario_novo'),
    path('propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/agricultura/', views.agricultura_dashboard, name='agricultura_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('propriedade/<int:propriedade_id>/patrimonio/', views.patrimonio_dashboard, name='patrimonio_dashboard'),
    path('propriedade/<int:propriedade_id>/projetos/', views.projetos_dashboard, name='projetos_dashboard'),
    path('propriedade/<int:propriedade_id>/relatorio/', views.relatorio_final, name='relatorio_final'),
]
"@ | Out-File -FilePath "gestao_rural/urls.py" -Encoding UTF8

# admin.py
@"
from django.contrib import admin
from .models import Proprietario, Propriedade, ProjetoCredito

@admin.register(Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'cidade', 'estado', 'created_at']
    search_fields = ['nome', 'cpf', 'cidade', 'email']
    list_filter = ['estado', 'cidade', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nome']

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'proprietario', 'area', 'municipio', 'estado', 'created_at']
    search_fields = ['nome', 'proprietario__nome', 'municipio', 'matricula']
    list_filter = ['estado', 'municipio', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['nome']

@admin.register(ProjetoCredito)
class ProjetoCreditoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'propriedade', 'tipo', 'valor_solicitado', 'status', 'data_inicio']
    search_fields = ['titulo', 'propriedade__nome', 'propriedade__proprietario__nome']
    list_filter = ['tipo', 'status', 'data_inicio', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
"@ | Out-File -FilePath "gestao_rural/admin.py" -Encoding UTF8

# 4. CRIAR TEMPLATES CLEAN
Write-Host "🎨 Criando templates com design clean..." -ForegroundColor Cyan

# Landing page clean
@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monpec Projetista - Sistema de Gestão Rural</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        .header {
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #004a99;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-links a {
            color: #666;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #004a99;
        }
        
        .btn-login {
            background: #004a99;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .btn-login:hover {
            background: #003366;
        }
        
        /* Hero */
        .hero {
            background: linear-gradient(135deg, #004a99 0%, #003366 100%);
            color: white;
            padding: 120px 0 80px;
            text-align: center;
        }
        
        .hero h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            line-height: 1.2;
        }
        
        .hero p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .btn-hero {
            background: #28a745;
            color: white;
            padding: 1rem 2rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 1.1rem;
            font-weight: 600;
            display: inline-block;
            transition: all 0.3s;
        }
        
        .btn-hero:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        
        /* Features */
        .features {
            padding: 80px 0;
            background: white;
        }
        
        .features h2 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: #333;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }
        
        .feature-card {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            transition: transform 0.3s;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
        }
        
        .feature-icon {
            width: 60px;
            height: 60px;
            background: #004a99;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            font-size: 1.5rem;
            color: white;
        }
        
        .feature-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .feature-desc {
            color: #666;
            line-height: 1.6;
        }
        
        /* CTA */
        .cta {
            background: #f8f9fa;
            padding: 80px 0;
            text-align: center;
        }
        
        .cta h2 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .cta p {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }
        
        /* Footer */
        .footer {
            background: #333;
            color: white;
            padding: 2rem 0;
            text-align: center;
        }
        
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2rem;
            }
            
            .nav-links {
                display: none;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <div class="logo">Monpec Projetista</div>
                <div class="nav-links">
                    <a href="#features">Funcionalidades</a>
                    <a href="#contact">Contato</a>
                </div>
                <a href="{% url 'login' %}" class="btn-login">Acessar Sistema</a>
            </nav>
        </div>
    </header>
    
    <section class="hero">
        <div class="container">
            <h1>Gestão Rural Inteligente</h1>
            <p>Automatize seus projetos de crédito rural com o sistema mais completo do mercado</p>
            <a href="{% url 'login' %}" class="btn-hero">Começar Agora</a>
        </div>
    </section>
    
    <section class="features" id="features">
        <div class="container">
            <h2>Funcionalidades</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Dashboard Inteligente</h3>
                    <p class="feature-desc">Acompanhe todos os seus projetos em tempo real com métricas e indicadores</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">👥</div>
                    <h3 class="feature-title">Gestão de Proprietários</h3>
                    <p class="feature-desc">Cadastre e gerencie todos os proprietários rurais de forma organizada</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🏡</div>
                    <h3 class="feature-title">Controle de Propriedades</h3>
                    <p class="feature-desc">Gerencie propriedades, áreas e documentação de forma centralizada</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📈</div>
                    <h3 class="feature-title">Módulos Especializados</h3>
                    <p class="feature-desc">Pecuária, Agricultura, Financeiro e Patrimônio em módulos integrados</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📋</div>
                    <h3 class="feature-title">Relatórios Automáticos</h3>
                    <p class="feature-desc">Gere relatórios e documentos automaticamente para seus clientes</p>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🔒</div>
                    <h3 class="feature-title">Segurança Total</h3>
                    <p class="feature-desc">Seus dados protegidos com criptografia e backup automático</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="cta">
        <div class="container">
            <h2>Pronto para revolucionar sua gestão?</h2>
            <p>Junte-se a centenas de projetistas que já automatizaram seus processos</p>
            <a href="{% url 'login' %}" class="btn-hero">Acessar Sistema</a>
        </div>
    </section>
    
    <footer class="footer" id="contact">
        <div class="container">
            <h3>Monpec Projetista</h3>
            <p>Sistema de Gestão Rural Inteligente</p>
            <p>contato@monpec.com.br | (67) 99999-9999</p>
            <p>&copy; 2024 Monpec Projetista. Todos os direitos reservados.</p>
        </div>
    </footer>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/landing.html" -Encoding UTF8

# Login clean
@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Monpec Projetista</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 3rem;
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        
        .logo {
            font-size: 2rem;
            font-weight: 700;
            color: #004a99;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
            text-align: left;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 600;
            color: #333;
        }
        
        .form-control {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-control:focus {
            outline: none;
            border-color: #004a99;
        }
        
        .btn-login {
            width: 100%;
            background: #004a99;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .btn-login:hover {
            background: #003366;
        }
        
        .back-link {
            position: absolute;
            top: 2rem;
            left: 2rem;
            color: #666;
            text-decoration: none;
            font-weight: 500;
        }
        
        .back-link:hover {
            color: #004a99;
        }
        
        .alert {
            padding: 0.75rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            font-size: 0.9rem;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
    </style>
</head>
<body>
    <a href="{% url 'landing_page' %}" class="back-link">← Voltar</a>
    
    <div class="login-container">
        <div class="logo">Monpec Projetista</div>
        <p class="subtitle">Faça login para acessar o sistema</p>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        
        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label for="username">Usuário</label>
                <input type="text" id="username" name="username" class="form-control" required>
            </div>
            
            <div class="form-group">
                <label for="password">Senha</label>
                <input type="password" id="password" name="password" class="form-control" required>
            </div>
            
            <button type="submit" class="btn-login">Entrar</button>
        </form>
    </div>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/login.html" -Encoding UTF8

# Dashboard clean
@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Monpec Projetista</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8f9fa;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        .header {
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1rem 0;
        }
        
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #004a99;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
        }
        
        .nav-links a {
            color: #666;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #004a99;
        }
        
        .user-menu {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .btn-logout {
            background: #dc3545;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 0.9rem;
        }
        
        .btn-logout:hover {
            background: #c82333;
        }
        
        /* Main Content */
        .main {
            padding: 2rem 0;
        }
        
        .page-header {
            margin-bottom: 2rem;
        }
        
        .page-header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .page-header p {
            color: #666;
            font-size: 1.1rem;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #004a99;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #666;
            font-size: 1rem;
        }
        
        /* Actions */
        .actions {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .actions h2 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .btn-group {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        
        .btn-primary {
            background: #004a99;
            color: white;
        }
        
        .btn-primary:hover {
            background: #003366;
            transform: translateY(-2px);
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
            transform: translateY(-2px);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .nav-links {
                display: none;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .btn-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <div class="logo">Monpec Projetista</div>
                <div class="nav-links">
                    <a href="{% url 'dashboard' %}">Dashboard</a>
                    <a href="{% url 'proprietarios_lista' %}">Proprietários</a>
                    <a href="{% url 'propriedades_lista' %}">Propriedades</a>
                </div>
                <div class="user-menu">
                    <span>Olá, {{ user.username }}</span>
                    <a href="{% url 'logout' %}" class="btn-logout">Sair</a>
                </div>
            </nav>
        </div>
    </header>
    
    <main class="main">
        <div class="container">
            <div class="page-header">
                <h1>Dashboard</h1>
                <p>Bem-vindo ao sistema de gestão rural</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ total_proprietarios }}</div>
                    <div class="stat-label">Proprietários</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ total_propriedades }}</div>
                    <div class="stat-label">Propriedades</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ total_projetos }}</div>
                    <div class="stat-label">Projetos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ projetos_aprovados }}</div>
                    <div class="stat-label">Aprovados</div>
                </div>
            </div>
            
            <div class="actions">
                <h2>Ações Rápidas</h2>
                <div class="btn-group">
                    <a href="{% url 'proprietario_novo' %}" class="btn btn-primary">Novo Proprietário</a>
                    <a href="{% url 'propriedades_lista' %}" class="btn btn-success">Ver Propriedades</a>
                    <a href="{% url 'proprietarios_lista' %}" class="btn btn-secondary">Listar Proprietários</a>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/dashboard.html" -Encoding UTF8

# 5. EXECUTAR COMANDOS DJANGO
Write-Host "🗄️ Configurando banco de dados..." -ForegroundColor Cyan

# Fazer migrações
Write-Host "📊 Criando migrações..." -ForegroundColor White
python manage.py makemigrations

Write-Host "🗃️ Aplicando migrações..." -ForegroundColor White
python manage.py migrate

# Criar superusuário automaticamente
Write-Host "👤 Criando superusuário..." -ForegroundColor White
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@monpec.com', 'admin123')" | python manage.py shell

# 6. INICIAR SERVIDOR
Write-Host ""
Write-Host "🎉 SISTEMA MONPEC CLEAN CRIADO!" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 INFORMAÇÕES:" -ForegroundColor Cyan
Write-Host "• URL: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "• Usuário: admin" -ForegroundColor White
Write-Host "• Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🎨 DESIGN CLEAN INCLUÍDO:" -ForegroundColor Cyan
Write-Host "✅ Interface limpa e moderna" -ForegroundColor Green
Write-Host "✅ Cores suaves e profissionais" -ForegroundColor Green
Write-Host "✅ Tipografia clean" -ForegroundColor Green
Write-Host "✅ Layout responsivo" -ForegroundColor Green
Write-Host "✅ Animações sutis" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor Django
python manage.py runserver


