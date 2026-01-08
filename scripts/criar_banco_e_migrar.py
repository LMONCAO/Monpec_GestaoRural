#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar banco de dados PostgreSQL e aplicar migracoes
"""
import os
import sys
import django
from decouple import config

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

def criar_banco():
    """Cria o banco de dados se não existir"""
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        db_name = config('DB_NAME', default='monpec_db_local')
        db_user = config('DB_USER', default='postgres')
        db_password = config('DB_PASSWORD', default='postgres')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')
        
        # Garantir que todos os valores sao strings validas
        db_name = str(db_name)
        db_user = str(db_user)
        db_password = str(db_password)
        db_host = str(db_host)
        db_port = str(db_port)
        
        print(f"Tentando conectar ao PostgreSQL...")
        print(f"  Host: {db_host}")
        print(f"  Porta: {db_port}")
        print(f"  Usuario: {db_user}")
        print(f"  Banco: {db_name}")
        print()
        
        try:
            # Conectar ao banco padrao 'postgres'
            # Usar connection string para evitar problemas de encoding
            conn_string = f"host='{db_host}' port='{db_port}' user='{db_user}' password='{db_password}' dbname='postgres'"
            conn = psycopg2.connect(conn_string)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Verificar se banco ja existe
            cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE {db_name}')
                print(f"[OK] Banco de dados '{db_name}' criado com sucesso!")
            else:
                print(f"[INFO] Banco de dados '{db_name}' ja existe.")
            
            cursor.close()
            conn.close()
            print("[OK] Conexao com PostgreSQL OK!")
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if 'Connection refused' in error_msg or 'could not connect' in error_msg.lower():
                print("[ERRO] PostgreSQL nao esta rodando ou nao esta acessivel.")
                print("   Verifique se o servico PostgreSQL esta iniciado.")
            elif 'password authentication failed' in error_msg.lower():
                print("[ERRO] Senha incorreta. Verifique DB_PASSWORD no arquivo .env")
            else:
                print(f"[ERRO] Erro de conexao: {error_msg}")
            return False
        except UnicodeDecodeError as e:
            print(f"[ERRO] Erro de codificacao ao conectar: {e}")
            print("[ERRO] Verifique se a senha no arquivo .env esta correta.")
            return False
        except Exception as e:
            print(f"[ERRO] Erro inesperado: {e}")
            return False
            
    except ImportError:
        print("[ERRO] psycopg2 nao esta instalado.")
        print("   Execute: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def aplicar_migracoes():
    """Aplica todas as migracoes"""
    print()
    print("=" * 50)
    print("Aplicando migracoes...")
    print("=" * 50)
    print()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate'])
    
    print()
    print("=" * 50)
    print("Verificando estado das migracoes...")
    print("=" * 50)
    print()
    
    from django.core.management import call_command
    call_command('showmigrations')

if __name__ == '__main__':
    print("=" * 50)
    print("Configuracao Automatica PostgreSQL")
    print("=" * 50)
    print()
    
    # Criar banco
    if criar_banco():
        # Aplicar migracoes
        aplicar_migracoes()
        print()
        print("=" * 50)
        print("[OK] Configuracao concluida!")
        print("=" * 50)
    else:
        print()
        print("=" * 50)
        print("[AVISO] Nao foi possivel configurar o banco.")
        print()
        print("Proximos passos:")
        print("  1. Instale PostgreSQL: https://www.postgresql.org/download/windows/")
        print("  2. Inicie o servico PostgreSQL")
        print("  3. Verifique as credenciais no arquivo .env")
        print("  4. Execute este script novamente")
        print("=" * 50)
        sys.exit(1)


