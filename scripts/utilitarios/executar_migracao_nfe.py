#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para aplicar a migração 0070_adicionar_cliente_nota_fiscal
Execute: python executar_migracao_nfe.py
"""

import os
import sys
import django

# Configurar Django
if __name__ == '__main__':
    # Adicionar o diretório do projeto ao path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Configurar settings do Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
    
    # Inicializar Django
    django.setup()
    
    # Executar migração
    from django.core.management import execute_from_command_line
    
    print("🔄 Aplicando migração de NF-e...")
    print("=" * 50)
    
    try:
        # Aplicar todas as migrações pendentes do app gestao_rural
        execute_from_command_line(['manage.py', 'migrate', 'gestao_rural'])
        print("\n✅ Migração aplicada com sucesso!")
        print("O campo 'cliente' foi adicionado à tabela NotaFiscal.")
    except Exception as e:
        print(f"\n❌ Erro ao aplicar migração: {e}")
        sys.exit(1)

