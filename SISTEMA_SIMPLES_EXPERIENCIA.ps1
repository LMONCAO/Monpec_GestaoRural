# ========================================
# SISTEMA SIMPLES - MELHOR EXPERIÊNCIA
# ========================================

Write-Host "🎯 CRIANDO SISTEMA SIMPLES E INTUITIVO" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Yellow

# 1. PARAR SERVIDOR
Write-Host "🛑 Parando servidor..." -ForegroundColor Cyan
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. CRIAR NOVO PROJETO LIMPO
Write-Host "📁 Criando projeto limpo..." -ForegroundColor Cyan
Remove-Item "monpec_simples" -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "monpec_simples" -Force
Set-Location "monpec_simples"

# 3. CRIAR ESTRUTURA
New-Item -ItemType Directory -Path "monpec_sistema" -Force
New-Item -ItemType Directory -Path "gestao_rural" -Force
New-Item -ItemType Directory -Path "templates" -Force
New-Item -ItemType Directory -Path "templates/gestao_rural" -Force
New-Item -ItemType Directory -Path "static" -Force
New-Item -ItemType Directory -Path "static/css" -Force
New-Item -ItemType Directory -Path "static/js" -Force

# 4. CRIAR ARQUIVOS DJANGO
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

# 5. CRIAR APP GESTAO_RURAL
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

class Proprietario(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Proprietário"
        verbose_name_plural = "Proprietários"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Propriedade(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Propriedade")
    proprietario = models.ForeignKey(Proprietario, on_delete=models.CASCADE, related_name='propriedades', verbose_name="Proprietário")
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Área (hectares)")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.proprietario.nome}"
"@ | Out-File -FilePath "gestao_rural/models.py" -Encoding UTF8

# views.py
@"
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from .models import Proprietario, Propriedade
import json

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
    
    context = {
        'total_proprietarios': total_proprietarios,
        'total_propriedades': total_propriedades,
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
    
    return render(request, 'gestao_rural/proprietarios_lista.html', {
        'proprietarios': proprietarios,
        'search': search
    })

@login_required
@csrf_exempt
def proprietario_novo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            cpf = data.get('cpf')
            telefone = data.get('telefone', '')
            email = data.get('email', '')
            cidade = data.get('cidade', '')
            estado = data.get('estado', '')
            
            if not nome or not cpf:
                return JsonResponse({'success': False, 'message': 'Nome e CPF são obrigatórios!'})
            
            if Proprietario.objects.filter(cpf=cpf).exists():
                return JsonResponse({'success': False, 'message': 'CPF já cadastrado!'})
            
            proprietario = Proprietario.objects.create(
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email,
                cidade=cidade,
                estado=estado
            )
            
            return JsonResponse({
                'success': True, 
                'message': f'Proprietário {nome} cadastrado com sucesso!',
                'proprietario': {
                    'id': proprietario.id,
                    'nome': proprietario.nome,
                    'cpf': proprietario.cpf,
                    'telefone': proprietario.telefone or '',
                    'email': proprietario.email or '',
                    'cidade': proprietario.cidade or '',
                    'estado': proprietario.estado or '',
                    'created_at': proprietario.created_at.strftime('%d/%m/%Y')
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Erro ao cadastrar: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def propriedades_lista(request):
    search = request.GET.get('search', '')
    propriedades = Propriedade.objects.select_related('proprietario')
    
    if search:
        propriedades = propriedades.filter(
            Q(nome__icontains=search) | 
            Q(proprietario__nome__icontains=search) |
            Q(municipio__icontains=search)
        )
    
    return render(request, 'gestao_rural/propriedades_lista.html', {
        'propriedades': propriedades,
        'search': search
    })
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
]
"@ | Out-File -FilePath "gestao_rural/urls.py" -Encoding UTF8

# admin.py
@"
from django.contrib import admin
from .models import Proprietario, Propriedade

@admin.register(Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf', 'cidade', 'estado', 'created_at']
    search_fields = ['nome', 'cpf', 'cidade', 'email']
    list_filter = ['estado', 'cidade', 'created_at']
    ordering = ['nome']

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'proprietario', 'area', 'municipio', 'estado', 'created_at']
    search_fields = ['nome', 'proprietario__nome', 'municipio']
    list_filter = ['estado', 'municipio', 'created_at']
    ordering = ['nome']
"@ | Out-File -FilePath "gestao_rural/admin.py" -Encoding UTF8

# 6. CRIAR TEMPLATES SIMPLES
Write-Host "🎨 Criando templates simples..." -ForegroundColor Cyan

# Landing page
@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monpec Projetista</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #333; }
        .hero { background: linear-gradient(135deg, #004a99 0%, #003366 100%); color: white; padding: 100px 0; text-align: center; }
        .hero h1 { font-size: 3rem; font-weight: 700; margin-bottom: 1rem; }
        .hero p { font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9; }
        .btn-hero { background: #28a745; color: white; padding: 1rem 2rem; border-radius: 6px; text-decoration: none; font-size: 1.1rem; font-weight: 600; display: inline-block; transition: all 0.3s; }
        .btn-hero:hover { background: #218838; transform: translateY(-2px); color: white; }
        .features { padding: 80px 0; background: white; }
        .features h2 { text-align: center; font-size: 2.5rem; margin-bottom: 3rem; color: #333; }
        .features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; }
        .feature-card { background: #f8f9fa; padding: 2rem; border-radius: 12px; text-align: center; transition: transform 0.3s; }
        .feature-card:hover { transform: translateY(-5px); }
        .feature-icon { width: 60px; height: 60px; background: #004a99; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-size: 1.5rem; color: white; }
        .feature-title { font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #333; }
        .feature-desc { color: #666; line-height: 1.6; }
        .footer { background: #333; color: white; padding: 2rem 0; text-align: center; }
    </style>
</head>
<body>
    <section class="hero">
        <div class="container">
            <h1>Monpec Projetista</h1>
            <p>Sistema de Gestão Rural Inteligente</p>
            <a href="{% url 'login' %}" class="btn-hero">Acessar Sistema</a>
        </div>
    </section>
    
    <section class="features">
        <div class="container">
            <h2>Funcionalidades</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">👥</div>
                    <h3 class="feature-title">Gestão de Proprietários</h3>
                    <p class="feature-desc">Cadastre e gerencie proprietários rurais de forma simples</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🏡</div>
                    <h3 class="feature-title">Controle de Propriedades</h3>
                    <p class="feature-desc">Gerencie propriedades e áreas de forma centralizada</p>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">Dashboard Inteligente</h3>
                    <p class="feature-desc">Acompanhe tudo em tempo real com métricas claras</p>
                </div>
            </div>
        </div>
    </section>
    
    <footer class="footer">
        <div class="container">
            <h3>Monpec Projetista</h3>
            <p>Sistema de Gestão Rural Inteligente</p>
            <p>&copy; 2024 Monpec Projetista. Todos os direitos reservados.</p>
        </div>
    </footer>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/landing.html" -Encoding UTF8

# Login page
@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Monpec Projetista</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .login-container { background: white; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); padding: 3rem; width: 100%; max-width: 400px; text-align: center; }
        .logo { font-size: 2rem; font-weight: 700; color: #004a99; margin-bottom: 0.5rem; }
        .subtitle { color: #666; margin-bottom: 2rem; font-size: 1rem; }
        .form-group { margin-bottom: 1.5rem; text-align: left; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }
        .form-control { width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem; transition: border-color 0.3s; }
        .form-control:focus { outline: none; border-color: #004a99; }
        .btn-login { width: 100%; background: #004a99; color: white; border: none; border-radius: 8px; padding: 0.75rem; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.3s; }
        .btn-login:hover { background: #003366; }
        .back-link { position: absolute; top: 2rem; left: 2rem; color: #666; text-decoration: none; font-weight: 500; }
        .back-link:hover { color: #004a99; }
        .alert { padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.9rem; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <a href="{% url 'landing_page' %}" class="back-link">← Voltar</a>
    
    <div class="login-container">
        <div class="logo">Monpec Projetista</div>
        <p class="subtitle">Faça login para acessar o sistema</p>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-error">{{ message }}</div>
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

# Dashboard
@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Monpec Projetista</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .header { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1rem 0; margin-bottom: 2rem; }
        .nav { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #004a99; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: #666; text-decoration: none; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: #004a99; }
        .user-menu { display: flex; align-items: center; gap: 1rem; }
        .btn-logout { background: #dc3545; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 0.9rem; }
        .page-header { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .page-header h1 { font-size: 2rem; font-weight: 700; color: #333; margin-bottom: 0.5rem; }
        .page-header p { color: #666; font-size: 1.1rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; transition: transform 0.3s; }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-number { font-size: 2.5rem; font-weight: 700; color: #004a99; margin-bottom: 0.5rem; }
        .stat-label { color: #666; font-size: 1rem; }
        .actions { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .actions h2 { font-size: 1.5rem; margin-bottom: 1rem; color: #333; }
        .btn-group { display: flex; gap: 1rem; flex-wrap: wrap; }
        .btn { padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s; border: none; cursor: pointer; }
        .btn-primary { background: #004a99; color: white; }
        .btn-primary:hover { background: #003366; transform: translateY(-2px); }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover { background: #218838; transform: translateY(-2px); }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover { background: #5a6268; transform: translateY(-2px); }
        @media (max-width: 768px) { .nav-links { display: none; } .stats-grid { grid-template-columns: 1fr; } .btn-group { flex-direction: column; } }
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
    
    <main>
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
            </div>
            
            <div class="actions">
                <h2>Ações Rápidas</h2>
                <div class="btn-group">
                    <a href="{% url 'proprietarios_lista' %}" class="btn btn-primary">Gerenciar Proprietários</a>
                    <a href="{% url 'propriedades_lista' %}" class="btn btn-success">Gerenciar Propriedades</a>
                </div>
            </div>
        </div>
    </main>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/dashboard.html" -Encoding UTF8

# Proprietários com popup
@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proprietários - Monpec Projetista</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .header { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1rem 0; margin-bottom: 2rem; }
        .nav { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #004a99; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: #666; text-decoration: none; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: #004a99; }
        .user-menu { display: flex; align-items: center; gap: 1rem; }
        .btn-logout { background: #dc3545; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 0.9rem; }
        .page-header { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .page-header h1 { font-size: 2rem; font-weight: 700; color: #333; margin-bottom: 0.5rem; }
        .page-header p { color: #666; font-size: 1.1rem; }
        .actions { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .actions h2 { font-size: 1.5rem; margin-bottom: 1rem; color: #333; }
        .btn-group { display: flex; gap: 1rem; flex-wrap: wrap; }
        .btn { padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s; border: none; cursor: pointer; }
        .btn-primary { background: #004a99; color: white; }
        .btn-primary:hover { background: #003366; transform: translateY(-2px); }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover { background: #5a6268; transform: translateY(-2px); }
        .search-form { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .search-form h3 { margin-bottom: 1rem; color: #333; }
        .form-group { display: flex; gap: 1rem; align-items: end; }
        .form-control { padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem; transition: border-color 0.3s; }
        .form-control:focus { outline: none; border-color: #004a99; }
        .proprietarios-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; }
        .proprietario-card { background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1.5rem; transition: transform 0.3s; }
        .proprietario-card:hover { transform: translateY(-5px); }
        .proprietario-header { border-bottom: 1px solid #e9ecef; padding-bottom: 1rem; margin-bottom: 1rem; }
        .proprietario-name { font-size: 1.25rem; font-weight: 600; color: #333; margin-bottom: 0.5rem; }
        .proprietario-cpf { color: #666; font-size: 0.9rem; }
        .proprietario-info { margin-bottom: 1rem; }
        .info-item { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .info-label { color: #666; font-weight: 500; }
        .info-value { color: #333; }
        .empty-state { text-align: center; padding: 3rem; color: #666; }
        .empty-state h3 { font-size: 1.5rem; margin-bottom: 1rem; color: #999; }
        
        /* POPUP STYLES */
        .popup-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: none; z-index: 1000; }
        .popup-overlay.active { display: flex; align-items: center; justify-content: center; }
        .popup { background: white; border-radius: 12px; padding: 2rem; width: 90%; max-width: 500px; max-height: 90vh; overflow-y: auto; }
        .popup-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
        .popup-title { font-size: 1.5rem; font-weight: 700; color: #333; }
        .popup-close { background: none; border: none; font-size: 1.5rem; color: #666; cursor: pointer; }
        .popup-close:hover { color: #333; }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }
        .form-control { width: 100%; padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem; transition: border-color 0.3s; }
        .form-control:focus { outline: none; border-color: #004a99; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .btn-group { display: flex; gap: 1rem; margin-top: 2rem; }
        .btn-success { background: #28a745; color: white; }
        .btn-success:hover { background: #218838; transform: translateY(-2px); }
        .alert { padding: 1rem; border-radius: 8px; margin-bottom: 1rem; font-weight: 500; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .loading { display: none; text-align: center; padding: 1rem; }
        .spinner { border: 3px solid #f3f3f3; border-top: 3px solid #004a99; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        @media (max-width: 768px) { .nav-links { display: none; } .proprietarios-grid { grid-template-columns: 1fr; } .form-group { flex-direction: column; } .form-row { grid-template-columns: 1fr; } }
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
    
    <main>
        <div class="container">
            <div class="page-header">
                <h1>Proprietários</h1>
                <p>Gerencie todos os proprietários rurais cadastrados</p>
            </div>
            
            <div class="actions">
                <h2>Ações</h2>
                <div class="btn-group">
                    <button onclick="abrirPopup()" class="btn btn-primary">Novo Proprietário</button>
                    <a href="{% url 'dashboard' %}" class="btn btn-secondary">Voltar ao Dashboard</a>
                </div>
            </div>
            
            <div class="search-form">
                <h3>Buscar Proprietários</h3>
                <form method="get">
                    <div class="form-group">
                        <input type="text" name="search" placeholder="Nome, CPF ou cidade..." class="form-control" value="{{ search }}">
                        <button type="submit" class="btn btn-primary">Buscar</button>
                    </div>
                </form>
            </div>
            
            <div id="proprietarios-container">
                {% if proprietarios %}
                    <div class="proprietarios-grid">
                        {% for proprietario in proprietarios %}
                        <div class="proprietario-card">
                            <div class="proprietario-header">
                                <div class="proprietario-name">{{ proprietario.nome }}</div>
                                <div class="proprietario-cpf">CPF: {{ proprietario.cpf }}</div>
                            </div>
                            
                            <div class="proprietario-info">
                                {% if proprietario.telefone %}
                                <div class="info-item">
                                    <span class="info-label">Telefone:</span>
                                    <span class="info-value">{{ proprietario.telefone }}</span>
                                </div>
                                {% endif %}
                                
                                {% if proprietario.email %}
                                <div class="info-item">
                                    <span class="info-label">Email:</span>
                                    <span class="info-value">{{ proprietario.email }}</span>
                                </div>
                                {% endif %}
                                
                                {% if proprietario.cidade %}
                                <div class="info-item">
                                    <span class="info-label">Cidade:</span>
                                    <span class="info-value">{{ proprietario.cidade }}, {{ proprietario.estado }}</span>
                                </div>
                                {% endif %}
                                
                                <div class="info-item">
                                    <span class="info-label">Propriedades:</span>
                                    <span class="info-value">{{ proprietario.propriedades.count }}</span>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="empty-state">
                        <h3>Nenhum proprietário encontrado</h3>
                        <p>Comece cadastrando seu primeiro proprietário</p>
                        <button onclick="abrirPopup()" class="btn btn-primary" style="margin-top: 1rem;">Cadastrar Primeiro Proprietário</button>
                    </div>
                {% endif %}
            </div>
        </div>
    </main>
    
    <!-- POPUP DE CADASTRO -->
    <div id="popup-overlay" class="popup-overlay">
        <div class="popup">
            <div class="popup-header">
                <h2 class="popup-title">Novo Proprietário</h2>
                <button class="popup-close" onclick="fecharPopup()">&times;</button>
            </div>
            
            <div id="alert-container"></div>
            
            <form id="form-proprietario">
                <div class="form-row">
                    <div class="form-group">
                        <label for="nome">Nome Completo *</label>
                        <input type="text" id="nome" name="nome" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="cpf">CPF *</label>
                        <input type="text" id="cpf" name="cpf" class="form-control" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="telefone">Telefone</label>
                        <input type="text" id="telefone" name="telefone" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="email">E-mail</label>
                        <input type="email" id="email" name="email" class="form-control">
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="cidade">Cidade</label>
                        <input type="text" id="cidade" name="cidade" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="estado">Estado</label>
                        <select id="estado" name="estado" class="form-control">
                            <option value="">Selecione</option>
                            <option value="MS">Mato Grosso do Sul</option>
                            <option value="MT">Mato Grosso</option>
                            <option value="GO">Goiás</option>
                            <option value="SP">São Paulo</option>
                            <option value="PR">Paraná</option>
                            <option value="RS">Rio Grande do Sul</option>
                            <option value="SC">Santa Catarina</option>
                            <option value="MG">Minas Gerais</option>
                            <option value="BA">Bahia</option>
                            <option value="DF">Distrito Federal</option>
                        </select>
                    </div>
                </div>
                
                <div class="btn-group">
                    <button type="submit" class="btn btn-success">Salvar Proprietário</button>
                    <button type="button" class="btn btn-secondary" onclick="fecharPopup()">Cancelar</button>
                </div>
            </form>
            
            <div id="loading" class="loading">
                <div class="spinner"></div>
                <p>Salvando proprietário...</p>
            </div>
        </div>
    </div>
    
    <script>
        function abrirPopup() {
            document.getElementById('popup-overlay').classList.add('active');
            document.getElementById('form-proprietario').reset();
            document.getElementById('alert-container').innerHTML = '';
        }
        
        function fecharPopup() {
            document.getElementById('popup-overlay').classList.remove('active');
        }
        
        document.getElementById('form-proprietario').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());
            
            // Mostrar loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('form-proprietario').style.display = 'none';
            
            fetch('{% url "proprietario_novo" %}', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('form-proprietario').style.display = 'block';
                
                if (data.success) {
                    // Mostrar sucesso
                    document.getElementById('alert-container').innerHTML = 
                        '<div class="alert alert-success">' + data.message + '</div>';
                    
                    // Fechar popup após 2 segundos
                    setTimeout(() => {
                        fecharPopup();
                        location.reload(); // Recarregar página para mostrar novo proprietário
                    }, 2000);
                } else {
                    // Mostrar erro
                    document.getElementById('alert-container').innerHTML = 
                        '<div class="alert alert-error">' + data.message + '</div>';
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('form-proprietario').style.display = 'block';
                document.getElementById('alert-container').innerHTML = 
                    '<div class="alert alert-error">Erro ao salvar proprietário. Tente novamente.</div>';
            });
        });
        
        // Fechar popup ao clicar fora
        document.getElementById('popup-overlay').addEventListener('click', function(e) {
            if (e.target === this) {
                fecharPopup();
            }
        });
    </script>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/proprietarios_lista.html" -Encoding UTF8

# Propriedades simples
@"
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Propriedades - Monpec Projetista</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8f9fa; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .header { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1rem 0; margin-bottom: 2rem; }
        .nav { display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #004a99; }
        .nav-links { display: flex; gap: 2rem; }
        .nav-links a { color: #666; text-decoration: none; font-weight: 500; transition: color 0.3s; }
        .nav-links a:hover { color: #004a99; }
        .user-menu { display: flex; align-items: center; gap: 1rem; }
        .btn-logout { background: #dc3545; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-decoration: none; font-size: 0.9rem; }
        .page-header { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .page-header h1 { font-size: 2rem; font-weight: 700; color: #333; margin-bottom: 0.5rem; }
        .page-header p { color: #666; font-size: 1.1rem; }
        .actions { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .actions h2 { font-size: 1.5rem; margin-bottom: 1rem; color: #333; }
        .btn-group { display: flex; gap: 1rem; flex-wrap: wrap; }
        .btn { padding: 0.75rem 1.5rem; border-radius: 8px; text-decoration: none; font-weight: 600; transition: all 0.3s; border: none; cursor: pointer; }
        .btn-primary { background: #004a99; color: white; }
        .btn-primary:hover { background: #003366; transform: translateY(-2px); }
        .btn-secondary { background: #6c757d; color: white; }
        .btn-secondary:hover { background: #5a6268; transform: translateY(-2px); }
        .search-form { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 2rem; }
        .search-form h3 { margin-bottom: 1rem; color: #333; }
        .form-group { display: flex; gap: 1rem; align-items: end; }
        .form-control { padding: 0.75rem; border: 2px solid #e9ecef; border-radius: 8px; font-size: 1rem; transition: border-color 0.3s; }
        .form-control:focus { outline: none; border-color: #004a99; }
        .propriedades-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }
        .propriedade-card { background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 1.5rem; transition: transform 0.3s; }
        .propriedade-card:hover { transform: translateY(-5px); }
        .propriedade-header { border-bottom: 1px solid #e9ecef; padding-bottom: 1rem; margin-bottom: 1rem; }
        .propriedade-name { font-size: 1.25rem; font-weight: 600; color: #333; margin-bottom: 0.5rem; }
        .propriedade-proprietario { color: #666; font-size: 0.9rem; }
        .propriedade-info { margin-bottom: 1rem; }
        .info-item { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .info-label { color: #666; font-weight: 500; }
        .info-value { color: #333; }
        .empty-state { text-align: center; padding: 3rem; color: #666; }
        .empty-state h3 { font-size: 1.5rem; margin-bottom: 1rem; color: #999; }
        @media (max-width: 768px) { .nav-links { display: none; } .propriedades-grid { grid-template-columns: 1fr; } .form-group { flex-direction: column; } }
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
    
    <main>
        <div class="container">
            <div class="page-header">
                <h1>Propriedades</h1>
                <p>Gerencie todas as propriedades rurais cadastradas</p>
            </div>
            
            <div class="actions">
                <h2>Ações</h2>
                <div class="btn-group">
                    <a href="{% url 'dashboard' %}" class="btn btn-secondary">Voltar ao Dashboard</a>
                    <a href="{% url 'proprietarios_lista' %}" class="btn btn-primary">Ver Proprietários</a>
                </div>
            </div>
            
            <div class="search-form">
                <h3>Buscar Propriedades</h3>
                <form method="get">
                    <div class="form-group">
                        <input type="text" name="search" placeholder="Nome da propriedade, proprietário ou município..." class="form-control" value="{{ search }}">
                        <button type="submit" class="btn btn-primary">Buscar</button>
                    </div>
                </form>
            </div>
            
            {% if propriedades %}
                <div class="propriedades-grid">
                    {% for propriedade in propriedades %}
                    <div class="propriedade-card">
                        <div class="propriedade-header">
                            <div class="propriedade-name">{{ propriedade.nome }}</div>
                            <div class="propriedade-proprietario">Proprietário: {{ propriedade.proprietario.nome }}</div>
                        </div>
                        
                        <div class="propriedade-info">
                            <div class="info-item">
                                <span class="info-label">Área:</span>
                                <span class="info-value">{{ propriedade.area }} hectares</span>
                            </div>
                            
                            <div class="info-item">
                                <span class="info-label">Município:</span>
                                <span class="info-value">{{ propriedade.municipio }}, {{ propriedade.estado }}</span>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="empty-state">
                    <h3>Nenhuma propriedade encontrada</h3>
                    <p>Comece cadastrando proprietários e suas propriedades</p>
                    <a href="{% url 'proprietarios_lista' %}" class="btn btn-primary" style="margin-top: 1rem;">Ver Proprietários</a>
                </div>
            {% endif %}
        </div>
    </main>
</body>
</html>
"@ | Out-File -FilePath "templates/gestao_rural/propriedades_lista.html" -Encoding UTF8

# 7. EXECUTAR COMANDOS DJANGO
Write-Host "🗄️ Configurando banco de dados..." -ForegroundColor Cyan

# Fazer migrações
Write-Host "📊 Criando migrações..." -ForegroundColor White
python manage.py makemigrations

Write-Host "🗃️ Aplicando migrações..." -ForegroundColor White
python manage.py migrate

# Criar superusuário automaticamente
Write-Host "👤 Criando superusuário..." -ForegroundColor White
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com', 'admin123')
    print('✅ Usuário admin criado!')
else:
    print('✅ Usuário admin já existe!')
"

# 8. INICIAR SERVIDOR
Write-Host ""
Write-Host "🎉 SISTEMA SIMPLES CRIADO!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 INFORMAÇÕES:" -ForegroundColor Cyan
Write-Host "• URL: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "• Usuário: admin" -ForegroundColor White
Write-Host "• Senha: admin123" -ForegroundColor White
Write-Host ""
Write-Host "🎯 FUNCIONALIDADES SIMPLES:" -ForegroundColor Cyan
Write-Host "✅ Dashboard limpo" -ForegroundColor Green
Write-Host "✅ Popup de cadastro de proprietários" -ForegroundColor Green
Write-Host "✅ Atualização em tempo real" -ForegroundColor Green
Write-Host "✅ Página de propriedades simples" -ForegroundColor Green
Write-Host "✅ Design clean e intuitivo" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 INICIANDO SERVIDOR..." -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

# Iniciar servidor
python manage.py runserver
