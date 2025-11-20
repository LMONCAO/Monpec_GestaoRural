#!/usr/bin/env python3
"""
Script para criar o sistema MONPEC PROJETISTA completo do zero
Gera estrutura limpa e organizada para desenvolvimento
"""

import os
import subprocess
import sys
from pathlib import Path

# Cores para output
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def print_step(step, message):
    print(f"\n{BLUE}[PASSO {step}]{RESET} {GREEN}{message}{RESET}")

def print_success(message):
    print(f"{GREEN}✓{RESET} {message}")

def print_error(message):
    print(f"{RED}✗{RESET} {message}")

def run_command(command, check=True):
    """Executa comando no shell"""
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Erro ao executar: {command}")
        print(e.stderr)
        return None

def create_file(filepath, content):
    """Cria arquivo com conteúdo"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print_success(f"Criado: {filepath}")

def main():
    print(f"\n{'='*60}")
    print(f"{GREEN}   CRIADOR DE SISTEMA MONPEC PROJETISTA{RESET}")
    print(f"{'='*60}\n")
    
    # Nome da pasta do projeto
    project_name = "monpec_projetista_clean"
    
    print_step(1, f"Criando estrutura na pasta: {project_name}")
    
    # Criar estrutura de diretórios
    directories = [
        f"{project_name}",
        f"{project_name}/monpec_project",
        f"{project_name}/monpec_project/monpec_project",
        f"{project_name}/gestao_rural",
        f"{project_name}/gestao_rural/migrations",
        f"{project_name}/gestao_rural/templates",
        f"{project_name}/gestao_rural/templates/gestao_rural",
        f"{project_name}/gestao_rural/templates/projetos_bancarios",
        f"{project_name}/static",
        f"{project_name}/static/css",
        f"{project_name}/static/js",
        f"{project_name}/static/images",
        f"{project_name}/media",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_success(f"Diretório: {directory}")
    
    print_step(2, "Criando arquivos do projeto Django")
    
    # Criar .gitignore
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    create_file(f"{project_name}/.gitignore", gitignore)
    
    # Criar requirements.txt
    requirements = """Django==4.2.7
Pillow==10.0.0
reportlab==4.0.4
openpyxl==3.1.2
matplotlib==3.7.2
numpy==1.24.3
"""
    create_file(f"{project_name}/requirements.txt", requirements)
    
    # Criar README.md
    readme = """# MONPEC PROJETISTA - Sistema de Gestão Rural

Sistema completo para elaboração de projetos bancários rurais.

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\\Scripts\\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

## Estrutura do Projeto

- `gestao_rural/` - App principal com todos os módulos
- `monpec_project/` - Configurações do Django
- `static/` - Arquivos estáticos (CSS, JS, imagens)
- `templates/` - Templates HTML

## Módulos

1. **Produtores e Propriedades** - Cadastro base
2. **Pecuária** - Gestão de rebanho com IA
3. **Agricultura** - Ciclos produtivos
4. **Bens e Patrimônio** - Gestão patrimonial
5. **Financeiro** - Custos e dívidas
6. **Projetos Bancários** - Consolidação e relatórios

## Desenvolvido com

- Django 4.2.7
- Python 3.11+
- Bootstrap 5
- ReportLab (PDF)
- OpenPyXL (Excel)
"""
    create_file(f"{project_name}/README.md", readme)
    
    print_step(3, "Criando configurações do Django")
    
    # Criar manage.py
    manage_py = """#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monpec_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"""
    create_file(f"{project_name}/manage.py", manage_py)
    
    # settings.py (simplificado, será expandido)
    settings = '''"""
Django settings for monpec_project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-change-this-in-production'
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

ROOT_URLCONF = 'monpec_project.urls'

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

WSGI_APPLICATION = 'monpec_project.wsgi.application'

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
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
'''
    create_file(f"{project_name}/monpec_project/settings.py", settings)
    
    # urls.py principal
    urls_main = '''from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestao_rural.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
'''
    create_file(f"{project_name}/monpec_project/urls.py", urls_main)
    
    # __init__.py para monpec_project
    create_file(f"{project_name}/monpec_project/__init__.py", "")
    
    # wsgi.py e asgi.py básicos
    wsgi_content = '''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monpec_project.settings')
application = get_wsgi_application()
'''
    create_file(f"{project_name}/monpec_project/wsgi.py", wsgi_content)
    create_file(f"{project_name}/monpec_project/asgi.py", wsgi_content.replace('wsgi', 'asgi').replace('WSGI', 'ASGI'))
    
    print_step(4, "Criando app gestao_rural")
    
    # __init__.py do app
    create_file(f"{project_name}/gestao_rural/__init__.py", "")
    
    # apps.py
    apps_content = '''from django.apps import AppConfig


class GestaoRuralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestao_rural'
'''
    create_file(f"{project_name}/gestao_rural/apps.py", apps_content)
    
    # admin.py básico
    create_file(f"{project_name}/gestao_rural/admin.py", "from django.contrib import admin\n# Register your models here.\n")
    
    # tests.py
    create_file(f"{project_name}/gestao_rural/tests.py", "from django.test import TestCase\n\n# Create your tests here.\n")
    
    # Criar arquivo __init__.py na pasta migrations
    create_file(f"{project_name}/gestao_rural/migrations/__init__.py", "")
    
    print_step(5, "Criando arquivo de consolidação financeira")
    
    # consolidacao_financeira.py
    consolidacao_content = '''# -*- coding: utf-8 -*-
"""
Módulo de Consolidação Financeira
Consolida dados de todos os módulos para análise bancária
"""

from .models import *


def consolidar_dados_propriedade(propriedade):
    """
    Consolida dados de todos os módulos da propriedade
    
    Args:
        propriedade: Objeto Propriedade
        
    Returns:
        dict: Dicionário com todos os dados consolidados
    """
    
    # Inicializar dicionário de retorno
    dados = {
        'pecuaria': {},
        'agricultura': {},
        'patrimonio': {},
        'financeiro': {},
        'consolidado': {},
    }
    
    # 1. PECUÁRIA
    try:
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        valor_rebanho = sum(item.valor_total for item in inventario)
        quantidade_total = sum(item.quantidade for item in inventario)
        
        dados['pecuaria'] = {
            'valor_total': valor_rebanho,
            'quantidade_total': quantidade_total,
            'itens': inventario,
        }
    except Exception as e:
        dados['pecuaria'] = {'valor_total': 0, 'quantidade_total': 0, 'itens': []}
    
    # 2. AGRICULTURA
    try:
        ciclos = CicloProducaoAgricola.objects.filter(propriedade=propriedade)
        receita_agricola = sum(ciclo.receita_esperada_total for ciclo in ciclos)
        
        dados['agricultura'] = {
            'receita_total': receita_agricola,
            'ciclos': ciclos,
        }
    except Exception as e:
        dados['agricultura'] = {'receita_total': 0, 'ciclos': []}
    
    # 3. PATRIMÔNIO
    try:
        bens = BemImobilizado.objects.filter(propriedade=propriedade, ativo=True)
        valor_patrimonio = sum(bem.valor_aquisicao for bem in bens)
        
        dados['patrimonio'] = {
            'valor_total': valor_patrimonio,
            'bens': bens,
        }
    except Exception as e:
        dados['patrimonio'] = {'valor_total': 0, 'bens': []}
    
    # 4. CUSTOS
    try:
        custos_fixos = CustoFixo.objects.filter(propriedade=propriedade, ativo=True)
        custos_variaveis = CustoVariavel.objects.filter(propriedade=propriedade, ativo=True)
        
        total_custos_fixos = sum(custo.custo_anual if hasattr(custo, 'custo_anual') else 0 
                                  for custo in custos_fixos)
        total_custos_variaveis = sum(custo.custo_anual if hasattr(custo, 'custo_anual') else 0 
                                      for custo in custos_variaveis)
        
        dados['financeiro'] = {
            'custos_fixos': total_custos_fixos,
            'custos_variaveis': total_custos_variaveis,
            'custos_totais': total_custos_fixos + total_custos_variaveis,
        }
    except Exception as e:
        dados['financeiro'] = {
            'custos_fixos': 0,
            'custos_variaveis': 0,
            'custos_totais': 0,
        }
    
    # 5. DÍVIDAS
    try:
        financiamentos = Financiamento.objects.filter(propriedade=propriedade, ativo=True)
        total_dividas = sum(f.valor_parcela * 12 for f in financiamentos)
        
        dados['financeiro']['dividas_totais'] = total_dividas
    except Exception as e:
        dados['financeiro']['dividas_totais'] = 0
    
    # CONSOLIDAÇÃO FINAL
    receita_pecuaria = dados['pecuaria']['valor_total'] * 0.15  # Estimativa 15% de vendas/ano
    receita_agricola = dados['agricultura']['receita_total']
    receita_total = receita_pecuaria + receita_agricola
    
    custos_totais = dados['financeiro']['custos_totais']
    lucro_bruto = receita_total - custos_totais
    
    dividas_totais = dados['financeiro']['dividas_totais']
    capacidade_pagamento = lucro_bruto - dividas_totais
    
    cobertura = receita_total / dividas_totais if dividas_totais > 0 else 0
    
    valor_patrimonio = dados['patrimonio']['valor_total']
    ltv = (dividas_totais / valor_patrimonio * 100) if valor_patrimonio > 0 else 0
    
    # Cálculo de score de risco (0-100)
    score = 0
    
    # Cobertura
    if cobertura > 3:
        score += 30
    elif cobertura > 1.5:
        score += 20
    else:
        score += 10 if cobertura > 0 else 0
    
    # LTV
    if ltv < 30:
        score += 30
    elif ltv < 60:
        score += 20
    else:
        score += 10 if ltv < 100 else 0
    
    # Diversificação
    if receita_pecuaria > 0 and receita_agricola > 0:
        score += 20
    
    # Capacidade positiva
    if capacidade_pagamento > 0:
        score += 20
    
    # Recomendação
    if score >= 80:
        recomendacao = "APROVAR"
        recomendacao_icon = "✅"
    elif score >= 60:
        recomendacao = "APROVAR COM CONDIÇÕES"
        recomendacao_icon = "⚠️"
    else:
        recomendacao = "REPROVAR"
        recomendacao_icon = "❌"
    
    dados['consolidado'] = {
        'receita_pecuaria': receita_pecuaria,
        'receita_agricola': receita_agricola,
        'receita_total': receita_total,
        'custos_totais': custos_totais,
        'lucro_bruto': lucro_bruto,
        'dividas_totais': dividas_totais,
        'capacidade_pagamento': capacidade_pagamento,
        'cobertura': cobertura,
        'valor_patrimonio': valor_patrimonio,
        'ltv': ltv,
        'score': score,
        'recomendacao': recomendacao,
        'recomendacao_icon': recomendacao_icon,
    }
    
    return dados
'''
    create_file(f"{project_name}/gestao_rural/consolidacao_financeira.py", consolidacao_content)
    
    print_step(6, "Script de criação concluído!")
    
    print(f"\n{'='*60}")
    print(f"{GREEN}✓ Sistema criado com sucesso em: {project_name}/{RESET}")
    print(f"{'='*60}\n")
    
    print(f"{YELLOW}Próximos passos:{RESET}")
    print(f"1. cd {project_name}")
    print(f"2. python -m venv venv")
    print(f"3. venv\\Scripts\\activate  (Windows)")
    print(f"4. pip install -r requirements.txt")
    print(f"5. python manage.py migrate")
    print(f"6. python manage.py createsuperuser")
    print(f"7. python manage.py runserver")
    print(f"\n{GREEN}Agora você precisa criar os models.py, views.py e templates!{RESET}\n")

if __name__ == "__main__":
    main()
