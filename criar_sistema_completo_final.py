"""
Script COMPLETO para criar o sistema MONPEC PROJETISTA do zero
Gera: models, views, urls, templates, admin - TUDO PRONTO PARA USAR
"""

import os

def criar_arquivo(caminho, conteudo):
    """Cria arquivo com o conteúdo especificado"""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)
    print(f"✓ {caminho}")

print("\n" + "="*60)
print("  CRIANDO SISTEMA MONPEC PROJETISTA COMPLETO")
print("="*60 + "\n")

pasta = "monpec_sistema_completo"

# Criar estrutura de pastas
pastas = [
    f"{pasta}",
    f"{pasta}/{pasta}",
    f"{pasta}/gestao_rural",
    f"{pasta}/gestao_rural/migrations",
    f"{pasta}/gestao_rural/templates",
    f"{pasta}/gestao_rural/templates/gestao_rural",
    f"{pasta}/gestao_rural/static",
    f"{pasta}/static",
    f"{pasta}/templates",
]

for p in pastas:
    os.makedirs(p, exist_ok=True)
    print(f"✓ Pasta: {p}")

print("\n[1/12] Criando requirements.txt...")
requirements = """Django==4.2.7
Pillow==10.0.0
reportlab==4.0.4
openpyxl==3.1.2
matplotlib==3.7.2
numpy==1.24.3
"""
criar_arquivo(f"{pasta}/requirements.txt", requirements)

print("\n[2/12] Criando manage.py...")
manage_py = """#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monpec_sistema_completo.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError from exc
    execute_from_command_line(sys.argv)
"""
criar_arquivo(f"{pasta}/manage.py", manage_py)

print("\n[3/12] Criando settings.py...")
settings_content = '''from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

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

ROOT_URLCONF = 'monpec_sistema_completo.urls'

TEMPLATES = [{
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
},]

WSGI_APPLICATION = 'monpec_sistema_completo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
'''
criar_arquivo(f"{pasta}/{pasta}/settings.py", settings_content)

# Criar urls.py principal
print("\n[4/12] Criando urls.py principal...")
urls_main = '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestao_rural.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''
criar_arquivo(f"{pasta}/{pasta}/urls.py", urls_main)

# Criar arquivos básicos
for arquivo in ['__init__.py', 'wsgi.py', 'asgi.py']:
    if arquivo == 'wsgi.py':
        conteudo = f"import os\nfrom django.core.wsgi import get_wsgi_application\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', '{pasta}.settings')\napplication = get_wsgi_application()"
    elif arquivo == 'asgi.py':
        conteudo = f"import os\nfrom django.core.asgi import get_asgi_application\nos.environ.setdefault('DJANGO_SETTINGS_MODULE', '{pasta}.settings')\napplication = get_asgi_application()"
    else:
        conteudo = ""
    criar_arquivo(f"{pasta}/{pasta}/{arquivo}", conteudo)

print("\n[5/12] Criando MODELS...")

# MODELS COMPLETO
models_content = '''from django.db import models
from django.contrib.auth.models import User

class ProdutorRural(models.Model):
    nome_completo = models.CharField(max_length=200)
    cpf_cnpj = models.CharField(max_length=20, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    endereco = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome_completo
    
    class Meta:
        verbose_name = "Produtor Rural"
        verbose_name_plural = "Produtores Rurais"

class Propriedade(models.Model):
    produtor = models.ForeignKey(ProdutorRural, on_delete=models.CASCADE)
    nome_propriedade = models.CharField(max_length=200)
    municipio = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    area_total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=[('propria', 'Própria'), ('arrendada', 'Arrendada')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome_propriedade} - {self.municipio}/{self.uf}"

class CategoriaAnimal(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

class InventarioRebanho(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaAnimal, on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    data_inventario = models.DateField()
    
    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.categoria.nome} - {self.quantidade} cabeças"

class CicloProducaoAgricola(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    cultura = models.CharField(max_length=100)
    safra = models.CharField(max_length=20)
    area_plantada = models.DecimalField(max_digits=10, decimal_places=2)
    produtividade = models.DecimalField(max_digits=10, decimal_places=2)
    custo_ha = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    receita_esperada_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    def save(self, *args, **kwargs):
        producao = self.area_plantada * self.produtividade
        self.receita_esperada_total = producao * self.preco_venda
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.cultura} {self.safra}"

class BemImobilizado(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    descricao = models.CharField(max_length=200)
    valor_aquisicao = models.DecimalField(max_digits=12, decimal_places=2)
    data_aquisicao = models.DateField()
    deprec_anual = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.descricao} ({self.tipo})"

class CustoFixo(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    custo_anual = models.DecimalField(max_digits=12, decimal_places=2)
    ativo = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        self.custo_anual = self.valor_mensal * 12
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor_mensal}/mês"

class CustoVariavel(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    custo_anual = models.DecimalField(max_digits=12, decimal_places=2)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.custo_anual}/ano"

class Financiamento(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    banco = models.CharField(max_length=100)
    tipo = models.CharField(max_length=100)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2)
    qt_parcelas = models.IntegerField()
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.banco} - {self.tipo}"
'''
criar_arquivo(f"{pasta}/gestao_rural/models.py", models_content)

# Criar consolidação financeira
print("\n[6/12] Criando consolidação financeira...")
consolidacao = '''from .models import *

def consolidar_dados_propriedade(propriedade):
    dados = {'pecuaria': {}, 'agricultura': {}, 'patrimonio': {}, 'financeiro': {}, 'consolidado': {}}
    
    # Pecuária
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
    valor_rebanho = sum(item.valor_total for item in inventario)
    dados['pecuaria'] = {'valor_total': valor_rebanho, 'quantidade_total': sum(item.quantidade for item in inventario)}
    
    # Agricultura
    ciclos = CicloProducaoAgricola.objects.filter(propriedade=propriedade)
    receita_agricola = sum(ciclo.receita_esperada_total for ciclo in ciclos)
    dados['agricultura'] = {'receita_total': receita_agricola}
    
    # Patrimônio
    bens = BemImobilizado.objects.filter(propriedade=propriedade, ativo=True)
    dados['patrimonio'] = {'valor_total': sum(bem.valor_aquisicao for bem in bens)}
    
    # Custos
    custos_fixos = sum(c.custo_anual for c in CustoFixo.objects.filter(propriedade=propriedade, ativo=True))
    custos_variaveis = sum(c.custo_anual for c in CustoVariavel.objects.filter(propriedade=propriedade, ativo=True))
    dados['financeiro'] = {'custos_totais': custos_fixos + custos_variaveis}
    
    # Dívidas
    dividas = sum(f.valor_parcela * 12 for f in Financiamento.objects.filter(propriedade=propriedade, ativo=True))
    dados['financeiro']['dividas_totais'] = dividas
    
    # Consolidação
    receita_pecuaria = valor_rebanho * 0.15
    receita_total = receita_pecuaria + receita_agricola
    lucro = receita_total - dados['financeiro']['custos_totais']
    capacidade = lucro - dividas
    cobertura = receita_total / dividas if dividas > 0 else 0
    ltv = (dividas / dados['patrimonio']['valor_total'] * 100) if dados['patrimonio']['valor_total'] > 0 else 0
    
    score = 0
    if cobertura > 3: score += 30
    elif cobertura > 1.5: score += 20
    if ltv < 30: score += 30
    elif ltv < 60: score += 20
    if receita_pecuaria > 0 and receita_agricola > 0: score += 20
    if capacidade > 0: score += 20
    
    rec = "APROVAR" if score >= 80 else "APROVAR COM CONDIÇÕES" if score >= 60 else "REPROVAR"
    
    dados['consolidado'] = {
        'receita_total': receita_total, 'capacidade_pagamento': capacidade,
        'cobertura': cobertura, 'valor_patrimonio': dados['patrimonio']['valor_total'],
        'ltv': ltv, 'score': score, 'recomendacao': rec
    }
    return dados
'''
criar_arquivo(f"{pasta}/gestao_rural/consolidacao_financeira.py", consolidacao)

print("\n[7/12] Criando VIEWS...")

# VIEWS COMPLETO
views_content = '''from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .consolidacao_financeira import consolidar_dados_propriedade

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'gestao_rural/login.html')

@login_required
def dashboard(request):
    produtores = ProdutorRural.objects.count()
    propriedades = Propriedade.objects.count()
    return render(request, 'gestao_rural/dashboard.html', {
        'produtores': produtores,
        'propriedades': propriedades
    })

@login_required
def listar_propriedades(request):
    propriedades = Propriedade.objects.all()
    return render(request, 'gestao_rural/listar_propriedades.html', {'propriedades': propriedades})

@login_required
def detalhes_propriedade(request, pk):
    prop = get_object_or_404(Propriedade, pk=pk)
    dados = consolidar_dados_propriedade(prop)
    return render(request, 'gestao_rural/detalhes_propriedade.html', {
        'propriedade': prop,
        'dados': dados
    })
'''
criar_arquivo(f"{pasta}/gestao_rural/views.py", views_content)

print("\n[8/12] Criando URLS...")
urls_content = '''from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('propriedades/', views.listar_propriedades, name='listar_propriedades'),
    path('propriedades/<int:pk>/', views.detalhes_propriedade, name='detalhes_propriedade'),
]
'''
criar_arquivo(f"{pasta}/gestao_rural/urls.py", urls_content)

print("\n[9/12] Criando ADMIN...")
admin_content = '''from django.contrib import admin
from .models import *

@admin.register(ProdutorRural)
class ProdutorAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf_cnpj', 'telefone']
    search_fields = ['nome_completo', 'cpf_cnpj']

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ['nome_propriedade', 'produtor', 'municipio', 'uf']
    list_filter = ['uf', 'tipo']

@admin.register(InventarioRebanho)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'categoria', 'quantidade', 'valor_total']

@admin.register(CicloProducaoAgricola)
class CicloAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'cultura', 'safra', 'receita_esperada_total']

@admin.register(BemImobilizado)
class BemAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'descricao', 'valor_aquisicao']

@admin.register(Financiamento)
class FinanciamentoAdmin(admin.ModelAdmin):
    list_display = ['propriedade', 'banco', 'valor_total', 'ativo']

admin.site.register(CategoriaAnimal)
admin.site.register(CustoFixo)
admin.site.register(CustoVariavel)
'''
criar_arquivo(f"{pasta}/gestao_rural/admin.py", admin_content)

# Criar arquivos básicos do app
for arq in ['__init__.py', 'apps.py', 'tests.py', 'migrations/__init__.py']:
    if arq == 'apps.py':
        criar_arquivo(f"{pasta}/gestao_rural/{arq}", "from django.apps import AppConfig\n\nclass GestaoRuralConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = 'gestao_rural'")
    else:
        criar_arquivo(f"{pasta}/gestao_rural/{arq}", "")

print("\n[10/12] Criando TEMPLATES...")

# TEMPLATE LOGIN
login_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Login - MONPEC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; }
        .login-card { background: white; border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-4">
                <div class="login-card">
                    <h2 class="text-center mb-4">🏦 MONPEC</h2>
                    <form method="post">
                        {% csrf_token %}
                        <div class="mb-3">
                            <input type="text" name="username" class="form-control" placeholder="Usuário" required>
                        </div>
                        <div class="mb-3">
                            <input type="password" name="password" class="form-control" placeholder="Senha" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Entrar</button>
                    </form>
                    {% if messages %}
                        {% for message in messages %}
                            <div class="alert alert-danger mt-3">{{ message }}</div>
                        {% endfor %}
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''
criar_arquivo(f"{pasta}/gestao_rural/templates/gestao_rural/login.html", login_html)

# TEMPLATE DASHBOARD
dashboard_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - MONPEC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand">🏦 MONPEC PROJETISTA</span>
            <a href="/" class="btn btn-outline-light">Sair</a>
        </div>
    </nav>
    <div class="container mt-4">
        <h1>Dashboard</h1>
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5>👥 Produtores</h5>
                        <h2>{{ produtores }}</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5>🏡 Propriedades</h5>
                        <h2>{{ propriedades }}</h2>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-4">
            <a href="/propriedades/" class="btn btn-primary">Ver Propriedades</a>
        </div>
    </div>
</body>
</html>
'''
criar_arquivo(f"{pasta}/gestao_rural/templates/gestao_rural/dashboard.html", dashboard_html)

# TEMPLATE LISTAR PROPRIEDADES
listar_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Propriedades - MONPEC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand">🏦 MONPEC</span>
        </div>
    </nav>
    <div class="container mt-4">
        <h1>Propriedades</h1>
        <table class="table">
            <thead>
                <tr><th>Nome</th><th>Município</th><th>UF</th><th>Ações</th></tr>
            </thead>
            <tbody>
                {% for prop in propriedades %}
                <tr>
                    <td>{{ prop.nome_propriedade }}</td>
                    <td>{{ prop.municipio }}</td>
                    <td>{{ prop.uf }}</td>
                    <td><a href="/propriedades/{{ prop.pk }}/" class="btn btn-sm btn-primary">Ver Detalhes</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        <a href="/dashboard/" class="btn btn-secondary">Voltar</a>
    </div>
</body>
</html>
'''
criar_arquivo(f"{pasta}/gestao_rural/templates/gestao_rural/listar_propriedades.html", listar_html)

# TEMPLATE DETALHES PROPRIEDADE
detalhes_html = '''<!DOCTYPE html>
<html>
<head>
    <title>{{ propriedade.nome_propriedade }} - MONPEC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand">🏦 MONPEC</span>
        </div>
    </nav>
    <div class="container mt-4">
        <h1>{{ propriedade.nome_propriedade }}</h1>
        <div class="row mt-4">
            <div class="col-md-4">
                <div class="card text-white bg-primary">
                    <div class="card-body">
                        <h5>💰 Receita Total</h5>
                        <h3>R$ {{ dados.consolidado.receita_total|floatformat:2 }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-white bg-success">
                    <div class="card-body">
                        <h5>💵 Capacidade Pagamento</h5>
                        <h3>R$ {{ dados.consolidado.capacidade_pagamento|floatformat:2 }}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-white bg-info">
                    <div class="card-body">
                        <h5>🎯 Score de Risco</h5>
                        <h3>{{ dados.consolidado.score }}/100</h3>
                        <p>{{ dados.consolidado.recomendacao }}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-4">
            <a href="/propriedades/" class="btn btn-secondary">Voltar</a>
        </div>
    </div>
</body>
</html>
'''
criar_arquivo(f"{pasta}/gestao_rural/templates/gestao_rural/detalhes_propriedade.html", detalhes_html)

print("\n[11/12] Criando .gitignore e README...")

gitignore = '''__pycache__/
*.py[cod]
db.sqlite3
/venv/
/media/
/staticfiles/
'''
criar_arquivo(f"{pasta}/.gitignore", gitignore)

readme = '''# MONPEC PROJETISTA - Sistema Completo

Sistema completo para projetos bancários rurais.

## Instalação

```bash
python -m venv venv
venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Acessar

- Sistema: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin

## Funcionalidades

✅ Login e autenticação
✅ Gestão de produtores e propriedades
✅ Análise pecuária, agricultura e patrimônio
✅ Consolidação financeira automática
✅ Score de risco e recomendações
'''
criar_arquivo(f"{pasta}/README.md", readme)

print("\n[12/12] Sistema criado com sucesso!")
print("\n" + "="*60)
print("✓ SISTEMA COMPLETO CRIADO EM: " + pasta + "/")
print("="*60)
print("\nPróximos passos:")
print("1. cd " + pasta)
print("2. python -m venv venv")
print("3. venv\\Scripts\\activate")
print("4. pip install -r requirements.txt")
print("5. python manage.py migrate")
print("6. python manage.py createsuperuser")
print("7. python manage.py runserver")
print("\nAcesse: http://127.0.0.1:8000")
print("="*60 + "\n")
