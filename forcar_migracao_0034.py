#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para forçar a aplicação da migração 0034 que cria a tabela AnexoLancamentoFinanceiro.
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection, transaction
from django.core.management import call_command
from django.core.management.base import CommandError

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

def migration_applied(migration_name):
    """Verifica se uma migração foi aplicada"""
    from django.db.migrations.recorder import MigrationRecorder
    recorder = MigrationRecorder(connection)
    return recorder.migration_qs.filter(
        app='gestao_rural',
        name=migration_name
    ).exists()

def create_table_manually():
    """Cria a tabela manualmente se a migração falhar"""
    table_name = 'gestao_rural_anexolancamentofinanceiro'
    
    print(f"\nTentando criar tabela '{table_name}' manualmente...")
    
    with connection.cursor() as cursor:
        if 'sqlite' in connection.settings_dict['ENGINE']:
            # SQL para SQLite
            sql = """
            CREATE TABLE IF NOT EXISTS gestao_rural_anexolancamentofinanceiro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                criado_em DATETIME NOT NULL,
                atualizado_em DATETIME NOT NULL,
                arquivo VARCHAR(100) NOT NULL,
                nome_original VARCHAR(255) NOT NULL,
                lancamento_id BIGINT NOT NULL REFERENCES gestao_rural_lancamentofinanceiro(id) ON DELETE CASCADE
            );
            """
            cursor.execute(sql)
            
            # Criar índices
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS gestao_rural_anexolancamentofinanceiro_lancamento_id ON gestao_rural_anexolancamentofinanceiro(lancamento_id);"
            )
            
            print(f"✓ Tabela '{table_name}' criada manualmente!")
            return True
        else:
            print("Criação manual só suportada para SQLite no momento.")
            return False

def main():
    table_name = 'gestao_rural_anexolancamentofinanceiro'
    migration_name = '0034_financeiro_reestruturado'
    
    print(f"\n{'='*60}")
    print("FORÇAR APLICAÇÃO DA MIGRAÇÃO 0034")
    print(f"{'='*60}\n")
    
    # Verificar se a tabela já existe
    if table_exists(table_name):
        print(f"✓ A tabela '{table_name}' já existe!")
        return 0
    
    print(f"✗ A tabela '{table_name}' NÃO existe.")
    
    # Verificar se a migração foi aplicada
    if migration_applied(migration_name):
        print(f"⚠ A migração '{migration_name}' está marcada como aplicada,")
        print(f"  mas a tabela não existe. Isso indica um problema.")
        print(f"\nTentando criar a tabela manualmente...")
        if create_table_manually():
            # Registrar a migração como aplicada se não estiver
            try:
                from django.db.migrations.recorder import MigrationRecorder
                recorder = MigrationRecorder(connection)
                if not migration_applied(migration_name):
                    recorder.record_applied('gestao_rural', migration_name)
                print(f"✓ Migração registrada como aplicada.")
                return 0
            except Exception as e:
                print(f"⚠ Erro ao registrar migração: {e}")
                print(f"  Mas a tabela foi criada. Você pode continuar.")
                return 0
        else:
            return 1
    
    # A migração já está aplicada, mas a tabela não existe
    # Isso pode acontecer se a tabela foi deletada ou se houve problema na criação
    print(f"\nA migração '{migration_name}' está marcada como aplicada,")
    print(f"mas a tabela não existe. Criando tabela diretamente...")
    print()
    
    # Criar tabela diretamente (sem rollback)
    if create_table_manually():
        print(f"\n✓ Tabela '{table_name}' criada com sucesso!")
        return 0
    else:
        print(f"\n✗ Não foi possível criar a tabela.")
        return 1
            
    except CommandError as e:
        print(f"\n✗ Erro ao aplicar migração: {e}")
        print(f"\nTentando criar a tabela manualmente...")
        if create_table_manually():
            return 0
        return 1
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\nTentando criar a tabela manualmente como último recurso...")
        if create_table_manually():
            return 0
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

