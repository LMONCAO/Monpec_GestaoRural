#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script SIMPLES para criar a tabela AnexoLancamentoFinanceiro diretamente.
Usa SQLite diretamente sem passar pelo Django ORM.
"""
import os
import sys
import sqlite3

# Obter caminho do banco de dados
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

# Configurar Django apenas para obter o caminho do banco
import django
django.setup()

from django.conf import settings

def main():
    table_name = 'gestao_rural_anexolancamentofinanceiro'
    db_path = settings.DATABASES['default']['NAME']
    
    print(f"\n{'='*60}")
    print("CRIAR TABELA ANEXOLANCAMENTOFINANCEIRO")
    print(f"{'='*60}\n")
    print(f"Banco de dados: {db_path}\n")
    
    if not os.path.exists(db_path):
        print(f"✗ ERRO: Banco de dados não encontrado em: {db_path}")
        return 1
    
    try:
        # Conectar ao SQLite diretamente
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela já existe
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if cursor.fetchone():
            print(f"✓ Tabela '{table_name}' já existe!")
            cursor.close()
            conn.close()
            return 0
        
        print(f"✗ Tabela '{table_name}' não existe.")
        print(f"\nCriando tabela...\n")
        
        # Criar a tabela
        cursor.execute("""
            CREATE TABLE gestao_rural_anexolancamentofinanceiro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                criado_em DATETIME NOT NULL,
                atualizado_em DATETIME NOT NULL,
                arquivo VARCHAR(100) NOT NULL,
                nome_original VARCHAR(255) NOT NULL DEFAULT '',
                lancamento_id BIGINT NOT NULL,
                FOREIGN KEY (lancamento_id) REFERENCES gestao_rural_lancamentofinanceiro(id) ON DELETE CASCADE
            )
        """)
        
        # Criar índice
        cursor.execute("""
            CREATE INDEX gestao_rural_anexolancamentofinanceiro_lancamento_id 
            ON gestao_rural_anexolancamentofinanceiro(lancamento_id)
        """)
        
        # Confirmar
        conn.commit()
        
        # Verificar se foi criada
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        if cursor.fetchone():
            print(f"✓ Tabela '{table_name}' criada com sucesso!")
            cursor.close()
            conn.close()
            return 0
        else:
            print(f"✗ Erro: Tabela não foi criada.")
            cursor.close()
            conn.close()
            return 1
            
    except sqlite3.OperationalError as e:
        if "already exists" in str(e).lower():
            print(f"✓ Tabela '{table_name}' já existe!")
            return 0
        else:
            print(f"✗ Erro SQLite: {e}")
            return 1
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nErro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

