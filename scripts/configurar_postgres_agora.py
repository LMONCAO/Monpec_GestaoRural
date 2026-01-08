#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para configurar PostgreSQL - pode ser executado de qualquer lugar
"""
import os
import sys
from pathlib import Path

# Tentar encontrar o diretório do projeto
possible_paths = [
    Path(__file__).parent if '__file__' in globals() else None,
    Path.cwd(),
    Path.home() / "Desktop" / "MonPO-Monitor de Plano Orçamentario" / "Monpec_GestaoRural",
]

project_dir = None
for path in possible_paths:
    if path and path.exists():
        manage_py = path / "manage.py"
        if manage_py.exists():
            project_dir = path
            break

if not project_dir:
    print("❌ Não foi possível encontrar o diretório do projeto.")
    print("   Execute este script do diretório do projeto ou ajuste os caminhos.")
    sys.exit(1)

# Mudar para o diretório do projeto
os.chdir(project_dir)
sys.path.insert(0, str(project_dir))

print(f"✅ Diretório do projeto: {project_dir}")
print()

# Agora executar a configuração
import django
from decouple import config

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
        
        print("=" * 50)
        print("Configuração Automática PostgreSQL")
        print("=" * 50)
        print()
        print(f"Tentando conectar ao PostgreSQL...")
        print(f"  Host: {db_host}")
        print(f"  Porta: {db_port}")
        print(f"  Usuário: {db_user}")
        print(f"  Banco: {db_name}")
        print()
        
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE {db_name}')
                print(f"✅ Banco de dados '{db_name}' criado com sucesso!")
            else:
                print(f"ℹ️  Banco de dados '{db_name}' já existe.")
            
            cursor.close()
            conn.close()
            print("✅ Conexão com PostgreSQL OK!")
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if 'Connection refused' in error_msg or 'could not connect' in error_msg.lower():
                print("❌ PostgreSQL não está rodando ou não está acessível.")
                print("   Verifique se o serviço PostgreSQL está iniciado.")
            elif 'password authentication failed' in error_msg.lower():
                print("❌ Senha incorreta. Verifique DB_PASSWORD no arquivo .env")
            else:
                print(f"❌ Erro de conexão: {error_msg}")
            return False
            
    except ImportError:
        print("❌ psycopg2 não está instalado.")
        print("   Execute: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def aplicar_migracoes():
    """Aplica todas as migrações"""
    print()
    print("=" * 50)
    print("Aplicando migrações...")
    print("=" * 50)
    print()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate'])
    
    print()
    print("=" * 50)
    print("Verificando estado das migrações...")
    print("=" * 50)
    print()
    
    from django.core.management import call_command
    call_command('showmigrations')

if __name__ == '__main__':
    if criar_banco():
        aplicar_migracoes()
        print()
        print("=" * 50)
        print("✅ Configuração concluída!")
        print("=" * 50)
    else:
        print()
        print("=" * 50)
        print("⚠️  Não foi possível configurar o banco.")
        print()
        print("Próximos passos:")
        print("  1. Verifique se PostgreSQL está instalado e rodando")
        print("  2. Verifique as credenciais no arquivo .env")
        print("  3. Execute este script novamente")
        print("=" * 50)
        sys.exit(1)


