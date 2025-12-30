#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar a tabela AnexoLancamentoFinanceiro se ela não existir.
Útil quando há problemas com migrações.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def table_exists(table_name):
    """Verifica se uma tabela existe no banco de dados"""
    with connection.cursor() as cursor:
        if 'sqlite' in connection.settings_dict['ENGINE']:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                [table_name]
            )
        else:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_name = %s",
                [table_name]
            )
        return cursor.fetchone() is not None

def main():
    table_name = 'gestao_rural_anexolancamentofinanceiro'
    
    print(f"\n{'='*60}")
    print("VERIFICAR E CRIAR TABELA ANEXOLANCAMENTOFINANCEIRO")
    print(f"{'='*60}\n")
    
    # Verificar se a tabela existe
    print(f"Verificando se a tabela '{table_name}' existe...")
    if table_exists(table_name):
        print(f"✓ A tabela '{table_name}' já existe!")
        return 0
    
    print(f"✗ A tabela '{table_name}' NÃO existe.")
    print("\nAplicando migrações para criar a tabela...")
    print()
    
    # Aplicar migrações
    try:
        execute_from_command_line(['manage.py', 'migrate', 'gestao_rural'])
        
        # Verificar novamente
        if table_exists(table_name):
            print(f"\n✓ Tabela '{table_name}' criada com sucesso!")
            return 0
        else:
            print(f"\n✗ Tabela '{table_name}' ainda não existe após aplicar migrações.")
            print("\nTentando criar migrações...")
            
            # Criar migrações
            execute_from_command_line(['manage.py', 'makemigrations'])
            
            # Aplicar novamente
            execute_from_command_line(['manage.py', 'migrate', 'gestao_rural'])
            
            if table_exists(table_name):
                print(f"\n✓ Tabela '{table_name}' criada com sucesso!")
                return 0
            else:
                print(f"\n✗ Não foi possível criar a tabela '{table_name}'.")
                print("\nVocê pode fazer o dump excluindo esta tabela:")
                print("python manage.py dumpdata --natural-foreign --natural-primary --exclude gestao_rural.AnexoLancamentoFinanceiro -o dados_backup.json")
                return 1
                
    except Exception as e:
        print(f"\n✗ Erro ao aplicar migrações: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())

