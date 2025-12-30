#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar a tabela AnexoLancamentoFinanceiro diretamente,
sem fazer rollback de migrações.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.db import connection, transaction
import sqlite3

def table_exists(table_name):
    """Verifica se uma tabela existe no banco de dados"""
    try:
        if 'sqlite' in connection.settings_dict['ENGINE']:
            # Usar conexão SQLite diretamente para evitar problema de formatação do Django
            db_path = connection.settings_dict['NAME']
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            result = cursor.fetchone() is not None
            cursor.close()
            conn.close()
            return result
        else:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_name = %s",
                    [table_name]
                )
                return cursor.fetchone() is not None
    except Exception as e:
        print(f"Erro ao verificar tabela: {e}")
        return False

def create_table_directly():
    """Cria a tabela diretamente no banco de dados"""
    table_name = 'gestao_rural_anexolancamentofinanceiro'
    
    if table_exists(table_name):
        print(f"✓ Tabela '{table_name}' já existe!")
        return True
    
    print(f"Criando tabela '{table_name}' diretamente...")
    
    if 'sqlite' in connection.settings_dict['ENGINE']:
        try:
            # Usar conexão SQLite diretamente
            db_path = connection.settings_dict['NAME']
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Criar a tabela
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gestao_rural_anexolancamentofinanceiro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    criado_em DATETIME NOT NULL,
                    atualizado_em DATETIME NOT NULL,
                    arquivo VARCHAR(100) NOT NULL,
                    nome_original VARCHAR(255) NOT NULL DEFAULT '',
                    lancamento_id BIGINT NOT NULL,
                    FOREIGN KEY (lancamento_id) REFERENCES gestao_rural_lancamentofinanceiro(id) ON DELETE CASCADE
                );
            """)
            
            # Criar índice
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS gestao_rural_anexolancamentofinanceiro_lancamento_id 
                ON gestao_rural_anexolancamentofinanceiro(lancamento_id);
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # Verificar se foi criada
            if table_exists(table_name):
                print(f"✓ Tabela '{table_name}' criada com sucesso!")
                return True
            else:
                print(f"✗ Tabela não foi criada.")
                return False
                
        except Exception as e:
            print(f"✗ Erro ao criar tabela: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("Este script só suporta SQLite no momento.")
        return False

def main():
    table_name = 'gestao_rural_anexolancamentofinanceiro'
    
    print(f"\n{'='*60}")
    print("CRIAR TABELA ANEXOLANCAMENTOFINANCEIRO DIRETAMENTE")
    print(f"{'='*60}\n")
    
    # Verificar se já existe
    if table_exists(table_name):
        print(f"✓ A tabela '{table_name}' já existe!")
        return 0
    
    print(f"✗ A tabela '{table_name}' não existe.")
    print(f"\nCriando tabela diretamente no banco de dados...")
    print(f"(Sem fazer rollback de migrações)\n")
    
    if create_table_directly():
        print(f"\n{'='*60}")
        print("✓ SUCESSO! Tabela criada.")
        print(f"{'='*60}")
        print(f"\nAgora você pode fazer o dump:")
        print(f"python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json")
        return 0
    else:
        print(f"\n{'='*60}")
        print("✗ FALHA! Não foi possível criar a tabela.")
        print(f"{'='*60}")
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

