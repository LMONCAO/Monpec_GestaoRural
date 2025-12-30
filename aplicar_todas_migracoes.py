#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para aplicar TODAS as migrações, forçando se necessário.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection
from django.core.management import call_command
from django.core.management.base import CommandError

def main():
    print(f"\n{'='*60}")
    print("APLICAR TODAS AS MIGRAÇÕES")
    print(f"{'='*60}\n")
    
    # 1. Criar migrações
    print("[1/3] Criando migrações...")
    try:
        call_command('makemigrations', verbosity=1)
        print("✓ Migrações criadas (ou já estavam atualizadas)")
    except Exception as e:
        print(f"⚠ Erro ao criar migrações: {e}")
    
    # 2. Aplicar migrações
    print("\n[2/3] Aplicando migrações...")
    try:
        call_command('migrate', verbosity=2, interactive=False)
        print("✓ Migrações aplicadas")
    except Exception as e:
        print(f"✗ Erro ao aplicar migrações: {e}")
        return 1
    
    # 3. Verificar tabela específica
    print("\n[3/3] Verificando tabela gestao_rural_anexolancamentofinanceiro...")
    table_name = 'gestao_rural_anexolancamentofinanceiro'
    
    with connection.cursor() as cursor:
        if 'sqlite' in connection.settings_dict['ENGINE']:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                [table_name]
            )
            exists = cursor.fetchone() is not None
        else:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_name = %s",
                [table_name]
            )
            exists = cursor.fetchone() is not None
    
    if exists:
        print(f"✓ Tabela '{table_name}' existe!")
        return 0
    else:
        print(f"✗ Tabela '{table_name}' AINDA NÃO existe!")
        print("\nTentando aplicar migração 0034 especificamente...")
        try:
            call_command('migrate', 'gestao_rural', '0034_financeiro_reestruturado', verbosity=2)
            
            # Verificar novamente
            with connection.cursor() as cursor:
                if 'sqlite' in connection.settings_dict['ENGINE']:
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        [table_name]
                    )
                    exists = cursor.fetchone() is not None
                else:
                    cursor.execute(
                        "SELECT table_name FROM information_schema.tables WHERE table_name = %s",
                        [table_name]
                    )
                    exists = cursor.fetchone() is not None
            
            if exists:
                print(f"✓ Tabela '{table_name}' criada após aplicar migração 0034!")
                return 0
            else:
                print(f"✗ Tabela ainda não existe. Execute: python forcar_migracao_0034.py")
                return 1
        except Exception as e:
            print(f"✗ Erro ao aplicar migração 0034: {e}")
            print(f"\nExecute: python forcar_migracao_0034.py")
            return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

