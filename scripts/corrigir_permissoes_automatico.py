#!/usr/bin/env python3
"""
Script para corrigir permissões do usuário monpec_user no PostgreSQL
via Cloud SQL Proxy ou conexão direta
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path

# Configurações
PROJECT_ID = "monpec-sistema-rural"
DB_INSTANCE = "monpec-db"
DB_NAME = "monpec_db"
DB_USER = "monpec_user"
CONNECTION_NAME = f"{PROJECT_ID}:us-central1:{DB_INSTANCE}"

# Script SQL para executar
SQL_COMMANDS = """
-- Conectar ao banco
\\c {db_name}

-- Garantir que o usuário tem permissões no schema public
GRANT USAGE ON SCHEMA public TO {db_user};
GRANT CREATE ON SCHEMA public TO {db_user};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO {db_user};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO {db_user};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO {db_user};

-- Conceder permissões em tabelas existentes
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {db_user};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {db_user};
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO {db_user};

-- Tornar o usuário owner do schema
ALTER SCHEMA public OWNER TO {db_user};

-- Verificar permissões
\\du {db_user}
\\dt
\\q
""".format(db_name=DB_NAME, db_user=DB_USER)

def main():
    print("=" * 60)
    print("  CORRIGINDO PERMISSÕES DO BANCO DE DADOS")
    print("=" * 60)
    print()
    
    print(f"[INFO] Projeto: {PROJECT_ID}")
    print(f"[INFO] Instância: {DB_INSTANCE}")
    print(f"[INFO] Banco: {DB_NAME}")
    print(f"[INFO] Usuário: {DB_USER}")
    print()
    
    # Criar arquivo SQL temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
        f.write(SQL_COMMANDS)
        sql_file = f.name
    
    print(f"[OK] Script SQL criado: {sql_file}")
    print()
    
    print("[INFO] Para executar este script, você tem duas opções:")
    print()
    print("OPÇÃO 1: Via gcloud sql connect (Recomendado)")
    print("-" * 60)
    print(f"gcloud sql connect {DB_INSTANCE} \\")
    print(f"    --user=postgres \\")
    print(f"    --project={PROJECT_ID} \\")
    print(f"    --database=postgres")
    print()
    print("No prompt do PostgreSQL, execute:")
    print(f"  \\i {sql_file}")
    print()
    print("Ou copie e cole os comandos SQL:")
    print("-" * 60)
    print(SQL_COMMANDS)
    print("-" * 60)
    print()
    
    print("OPÇÃO 2: Execute o script Windows:")
    print("  CORRIGIR_PERMISSOES_BANCO_AUTOMATICO.bat")
    print()
    
    print("OPÇÃO 3: Execute o script Shell (no Cloud Shell):")
    print("  bash CORRIGIR_PERMISSOES_VIA_CLOUD_SHELL.sh")
    print()
    
    print("=" * 60)
    print("  IMPORTANTE")
    print("=" * 60)
    print("Este script não pode executar comandos SQL diretamente")
    print("porque requer autenticação do usuário postgres (superuser).")
    print("Execute uma das opções acima manualmente.")
    print()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())



