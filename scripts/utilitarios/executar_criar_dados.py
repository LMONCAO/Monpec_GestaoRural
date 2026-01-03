#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script temporário para executar o comando de criar dados
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monpec.settings')

try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    sys.exit(1)

# Importar e executar o comando
from django.core.management import call_command

if __name__ == '__main__':
    try:
        print("🚀 Executando comando criar_dados_dashboard_propriedade...")
        call_command('criar_dados_dashboard_propriedade', propriedade_id=19, verbosity=2)
        print("\n✅ Comando executado com sucesso!")
    except Exception as e:
        print(f"\n❌ Erro ao executar comando: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)















