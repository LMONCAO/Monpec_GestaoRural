#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para aplicar migrations de NF-e
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    sys.exit(1)

from django.core.management import call_command

def main():
    print("=" * 60)
    print("Aplicando Migrations de NF-e")
    print("=" * 60)
    print()
    
    try:
        print("Aplicando migrations do app gestao_rural...")
        call_command('migrate', 'gestao_rural', verbosity=2, interactive=False)
        
        print()
        print("=" * 60)
        print("✅ Migrations aplicadas com sucesso!")
        print("=" * 60)
        print()
        print("Reinicie o servidor Django para aplicar as mudanças.")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Erro ao aplicar migrations:")
        print("=" * 60)
        print(str(e))
        import traceback
        traceback.print_exc()
        print()
        sys.exit(1)

if __name__ == '__main__':
    main()




















