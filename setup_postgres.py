#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar banco PostgreSQL e aplicar migrações
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decouple import config

def criar_banco():
    """Cria o banco de dados se não existir"""
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        db_name = config('DB_NAME', default='monpec_db_local')
        db_user = config('DB_USER', default='postgres')
        # Ler senha como string raw para evitar problemas de encoding
        db_password = str(config('DB_PASSWORD', default='postgres'))
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')
        
        print("=" * 60)
        print("CONFIGURACAO AUTOMATICA POSTGRESQL")
        print("=" * 60)
        print()
        print(f"Conectando ao PostgreSQL...")
        print(f"  Host: {db_host}")
        print(f"  Porta: {db_port}")
        print(f"  Usuario: {db_user}")
        print(f"  Banco: {db_name}")
        print()
        
        try:
            # Conectar ao banco padrão 'postgres'
            # Usar parâmetros nomeados para evitar problemas de encoding na string
            import urllib.parse
            # Codificar a senha se necessário
            try:
                # Tentar conexão direta primeiro
                conn = psycopg2.connect(
                    host=db_host,
                    port=int(db_port),
                    user=db_user,
                    password=db_password.encode('utf-8').decode('utf-8') if isinstance(db_password, str) else str(db_password),
                    database='postgres',
                    client_encoding='UTF8'
                )
            except (UnicodeDecodeError, UnicodeEncodeError):
                # Se falhar, tentar com string de conexão codificada
                password_encoded = urllib.parse.quote_plus(str(db_password))
                conn_string = f"host={db_host} port={db_port} user={db_user} password={password_encoded} dbname=postgres"
                conn = psycopg2.connect(conn_string)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Verificar se banco já existe
            cursor.execute('SELECT 1 FROM pg_database WHERE datname = %s', (db_name,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE {db_name}')
                print(f"SUCCESS: Banco de dados '{db_name}' criado com sucesso!")
            else:
                print(f"INFO: Banco de dados '{db_name}' ja existe.")
            
            cursor.close()
            conn.close()
            print("SUCCESS: Conexao com PostgreSQL OK!")
            return True
            
        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if 'Connection refused' in error_msg or 'could not connect' in error_msg.lower():
                print("ERRO: PostgreSQL nao esta rodando ou nao esta acessivel.")
                print("   Verifique se o servico PostgreSQL esta iniciado.")
            elif 'password authentication failed' in error_msg.lower():
                print("ERRO: Senha incorreta. Verifique DB_PASSWORD no arquivo .env")
            else:
                print(f"ERRO de conexao: {error_msg}")
            return False
        except UnicodeDecodeError as e:
            print("ERRO: Problema com encoding da senha.")
            print("   Tente usar apenas caracteres ASCII na senha ou verifique o arquivo .env")
            return False
            
    except ImportError:
        print("ERRO: psycopg2 nao esta instalado.")
        print("   Execute: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def aplicar_migracoes():
    """Aplica todas as migrações"""
    print()
    print("=" * 60)
    print("APLICANDO MIGRACOES...")
    print("=" * 60)
    print()
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate'])
    
    print()
    print("=" * 60)
    print("VERIFICANDO ESTADO DAS MIGRACOES...")
    print("=" * 60)
    print()
    
    from django.core.management import call_command
    call_command('showmigrations')

if __name__ == '__main__':
    if criar_banco():
        aplicar_migracoes()
        print()
        print("=" * 60)
        print("SUCCESS: CONFIGURACAO CONCLUIDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("Todas as migracoes foram aplicadas!")
        print("O banco PostgreSQL esta configurado e pronto para uso.")
    else:
        print()
        print("=" * 60)
        print("AVISO: NAO FOI POSSIVEL CONFIGURAR O BANCO")
        print("=" * 60)
        print()
        print("Próximos passos:")
        print("  1. Verifique se PostgreSQL está instalado e rodando")
        print("  2. Verifique as credenciais no arquivo .env")
        print("  3. Execute este script novamente")
        print("=" * 60)
        sys.exit(1)

