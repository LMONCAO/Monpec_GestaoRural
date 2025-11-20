#!/usr/bin/env python
"""Script de diagnóstico do sistema"""
import os
import sys
import traceback

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("DIAGNÓSTICO DO SISTEMA MONPEC")
print("=" * 60)
print()

# Teste 1: Verificar Django
print("1. Verificando Django...")
try:
    import django
    print(f"   ✓ Django {django.get_version()} instalado")
except ImportError as e:
    print(f"   ✗ Erro ao importar Django: {e}")
    sys.exit(1)

# Teste 2: Configurar Django
print("\n2. Configurando Django...")
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
    django.setup()
    print("   ✓ Django configurado")
except Exception as e:
    print(f"   ✗ Erro ao configurar Django: {e}")
    traceback.print_exc()
    sys.exit(1)

# Teste 3: Verificar settings
print("\n3. Verificando settings...")
try:
    from django.conf import settings
    print(f"   ✓ SECRET_KEY: {settings.SECRET_KEY[:20]}...")
    print(f"   ✓ DEBUG: {settings.DEBUG}")
    print(f"   ✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
except Exception as e:
    print(f"   ✗ Erro ao verificar settings: {e}")
    traceback.print_exc()
    sys.exit(1)

# Teste 4: Verificar banco de dados
print("\n4. Verificando banco de dados...")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("   ✓ Conexão com banco de dados OK")
except Exception as e:
    print(f"   ✗ Erro na conexão com banco de dados: {e}")
    traceback.print_exc()

# Teste 5: Verificar apps instaladas
print("\n5. Verificando apps instaladas...")
try:
    from django.conf import settings
    print(f"   ✓ Apps instaladas: {len(settings.INSTALLED_APPS)}")
    for app in settings.INSTALLED_APPS:
        print(f"      - {app}")
except Exception as e:
    print(f"   ✗ Erro ao verificar apps: {e}")
    traceback.print_exc()

# Teste 6: Verificar URLs
print("\n6. Verificando URLs...")
try:
    from django.urls import get_resolver
    resolver = get_resolver()
    print(f"   ✓ Sistema de URLs carregado")
    print(f"   ✓ Total de padrões de URL: {len(list(resolver.url_patterns))}")
except Exception as e:
    print(f"   ✗ Erro ao verificar URLs: {e}")
    traceback.print_exc()

# Teste 7: Verificar importações de módulos
print("\n7. Verificando importações de módulos...")
modulos = [
    'gestao_rural.urls_vendas',
    'gestao_rural.urls_endividamento',
    'gestao_rural.urls_analise',
    'gestao_rural.urls_relatorios',
    'gestao_rural.urls_projetos_bancarios',
    'gestao_rural.urls_imobilizado',
    'gestao_rural.urls_capacidade_pagamento',
    'gestao_rural.urls_proprietario',
]

for modulo in modulos:
    try:
        __import__(modulo)
        print(f"   ✓ {modulo}")
    except Exception as e:
        print(f"   ✗ {modulo}: {e}")

# Teste 8: Verificar views
print("\n8. Verificando views principais...")
views_teste = [
    'gestao_rural.views',
    'gestao_rural.views_vendas',
    'gestao_rural.views_analise',
]

for view_module in views_teste:
    try:
        module = __import__(view_module, fromlist=[''])
        print(f"   ✓ {view_module}")
    except Exception as e:
        print(f"   ✗ {view_module}: {e}")

print("\n" + "=" * 60)
print("DIAGNÓSTICO CONCLUÍDO")
print("=" * 60)

















