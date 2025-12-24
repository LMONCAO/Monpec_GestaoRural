#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar e aplicar migrações pendentes
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command
from django.db import connection

def verificar_migracoes():
    """Verifica migrações pendentes"""
    print("=" * 70)
    print("VERIFICAÇÃO DE MIGRAÇÕES")
    print("=" * 70)
    print()
    
    try:
        # Mostrar status das migrações
        print("📋 Status das migrações:")
        print()
        call_command('showmigrations', 'gestao_rural', verbosity=1)
        
        print()
        print("=" * 70)
        print("Para aplicar migrações pendentes, execute:")
        print("   python manage.py migrate")
        print("=" * 70)
        
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar migrações: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    verificar_migracoes()












