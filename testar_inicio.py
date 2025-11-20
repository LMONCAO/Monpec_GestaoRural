#!/usr/bin/env python
"""Script para testar inicialização do servidor"""
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

try:
    import django
    django.setup()
    
    print("Django configurado com sucesso!")
    print("\nTestando importação de views...")
    
    # Testar importações principais
    try:
        from gestao_rural import views
        print("✓ gestao_rural.views")
    except Exception as e:
        print(f"✗ gestao_rural.views: {e}")
    
    try:
        from gestao_rural import views_vendas
        print("✓ gestao_rural.views_vendas")
    except Exception as e:
        print(f"✗ gestao_rural.views_vendas: {e}")
    
    try:
        from gestao_rural import urls
        print("✓ gestao_rural.urls")
    except Exception as e:
        print(f"✗ gestao_rural.urls: {e}")
    
    print("\nTentando iniciar servidor de teste...")
    from django.core.management import execute_from_command_line
    
    # Executar runserver em modo de teste
    sys.argv = ['manage.py', 'runserver', '--noreload']
    print("Executando: python manage.py runserver --noreload")
    
    # Executar
    execute_from_command_line(sys.argv)
    
except Exception as e:
    print(f"\nERRO CRÍTICO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

















