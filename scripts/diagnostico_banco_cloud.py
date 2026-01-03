#!/usr/bin/env python
"""
Script de diagnóstico para problemas de banco de dados no Google Cloud
Verifica configurações, permissões e conectividade
"""
import os
import sys
import django
from pathlib import Path

# Adicionar o diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

import logging
from django.db import connection
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verificar_variaveis_ambiente():
    """Verifica se todas as variáveis de ambiente necessárias estão definidas"""
    print("\n" + "="*60)
    print("1. VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("="*60)
    
    variaveis = {
        'CLOUD_SQL_CONNECTION_NAME': os.getenv('CLOUD_SQL_CONNECTION_NAME', ''),
        'DB_NAME': os.getenv('DB_NAME', ''),
        'DB_USER': os.getenv('DB_USER', ''),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
        'GOOGLE_CLOUD_PROJECT': os.getenv('GOOGLE_CLOUD_PROJECT', ''),
        'K_SERVICE': os.getenv('K_SERVICE', ''),
    }
    
    todas_ok = True
    for var, valor in variaveis.items():
        if var == 'DB_PASSWORD':
            status = "✅ DEFINIDO" if valor else "❌ NÃO DEFINIDO"
            print(f"   {var}: {status}")
        else:
            status = "✅ DEFINIDO" if valor else "❌ NÃO DEFINIDO"
            print(f"   {var}: {valor if valor else status}")
            if not valor and var in ['CLOUD_SQL_CONNECTION_NAME', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']:
                todas_ok = False
    
    return todas_ok

def verificar_configuracao_django():
    """Verifica a configuração do banco de dados no Django"""
    print("\n" + "="*60)
    print("2. VERIFICANDO CONFIGURAÇÃO DO DJANGO")
    print("="*60)
    
    db_config = settings.DATABASES['default']
    print(f"   ENGINE: {db_config.get('ENGINE')}")
    print(f"   NAME: {db_config.get('NAME')}")
    print(f"   USER: {db_config.get('USER')}")
    print(f"   HOST: {db_config.get('HOST', 'NÃO DEFINIDO')}")
    print(f"   PORT: {db_config.get('PORT', 'NÃO DEFINIDO')}")
    print(f"   PASSWORD: {'DEFINIDO' if db_config.get('PASSWORD') else 'NÃO DEFINIDO'}")
    
    # Verificar se está usando Unix Socket
    if db_config.get('HOST', '').startswith('/cloudsql/'):
        print(f"   ✅ Usando Unix Socket (Cloud SQL)")
        connection_name = db_config['HOST'].replace('/cloudsql/', '')
        print(f"   Connection Name: {connection_name}")
        
        # Validar formato
        if ':' in connection_name and connection_name.count(':') == 2:
            parts = connection_name.split(':')
            print(f"   ✅ Formato válido: PROJECT={parts[0]}, REGION={parts[1]}, INSTANCE={parts[2]}")
        else:
            print(f"   ❌ Formato inválido! Esperado: PROJECT:REGION:INSTANCE")
            return False
    else:
        print(f"   ⚠️ Usando conexão TCP/IP (não é Unix Socket)")
    
    return True

def testar_conexao():
    """Testa a conexão com o banco de dados"""
    print("\n" + "="*60)
    print("3. TESTANDO CONEXÃO COM O BANCO DE DADOS")
    print("="*60)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"   ✅ Conexão bem-sucedida!")
            print(f"   PostgreSQL Version: {version[0][:50]}...")
            
            # Testar query simples
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            print(f"   Database atual: {db_info[0]}")
            print(f"   Usuário atual: {db_info[1]}")
            
            return True
    except Exception as e:
        print(f"   ❌ ERRO ao conectar ao banco de dados!")
        print(f"   Tipo do erro: {type(e).__name__}")
        print(f"   Mensagem: {str(e)}")
        
        # Diagnóstico específico
        error_str = str(e).lower()
        if 'connection refused' in error_str or 'could not connect' in error_str:
            print("\n   🔍 DIAGNÓSTICO: Problema de conectividade")
            print("   Possíveis causas:")
            print("   1. Cloud SQL instance não está rodando")
            print("   2. Permissões IAM não configuradas corretamente")
            print("   3. Cloud SQL não está na mesma VPC do Cloud Run")
            print("   4. CLOUD_SQL_CONNECTION_NAME está incorreto")
        elif 'authentication failed' in error_str or 'password' in error_str:
            print("\n   🔍 DIAGNÓSTICO: Problema de autenticação")
            print("   Possíveis causas:")
            print("   1. DB_USER ou DB_PASSWORD incorretos")
            print("   2. Usuário não existe no banco de dados")
            print("   3. Senha expirada ou inválida")
        elif 'database' in error_str and 'does not exist' in error_str:
            print("\n   🔍 DIAGNÓSTICO: Banco de dados não existe")
            print("   Solução: Criar o banco de dados no Cloud SQL")
        elif 'permission denied' in error_str or 'access denied' in error_str:
            print("\n   🔍 DIAGNÓSTICO: Problema de permissões")
            print("   Possíveis causas:")
            print("   1. Usuário não tem permissões no banco")
            print("   2. Role IAM 'Cloud SQL Client' não está atribuída ao Cloud Run service account")
        
        return False

def verificar_arquivo_socket():
    """Verifica se o arquivo Unix Socket existe (apenas para Cloud Run)"""
    print("\n" + "="*60)
    print("4. VERIFICANDO ARQUIVO UNIX SOCKET")
    print("="*60)
    
    db_config = settings.DATABASES['default']
    host = db_config.get('HOST', '')
    
    if host.startswith('/cloudsql/'):
        socket_path = host
        if os.path.exists(socket_path):
            print(f"   ✅ Socket encontrado: {socket_path}")
            print(f"   Permissões: {oct(os.stat(socket_path).st_mode)[-3:]}")
            return True
        else:
            print(f"   ❌ Socket NÃO encontrado: {socket_path}")
            print("\n   🔍 DIAGNÓSTICO:")
            print("   O arquivo Unix Socket não existe. Isso pode indicar:")
            print("   1. Cloud SQL instance não está configurada corretamente")
            print("   2. Cloud Run não tem permissão para acessar o Cloud SQL")
            print("   3. --add-cloudsql-instances não foi usado no deploy")
            print("   4. Cloud SQL Auth Proxy não está rodando (se usando localmente)")
            return False
    else:
        print("   ⚠️ Não está usando Unix Socket (usando TCP/IP)")
        return None

def main():
    """Executa todos os diagnósticos"""
    print("\n" + "="*60)
    print("DIAGNÓSTICO DE BANCO DE DADOS - GOOGLE CLOUD")
    print("="*60)
    
    resultados = {
        'variaveis': verificar_variaveis_ambiente(),
        'configuracao': verificar_configuracao_django(),
        'socket': verificar_arquivo_socket(),
        'conexao': testar_conexao(),
    }
    
    print("\n" + "="*60)
    print("RESUMO")
    print("="*60)
    
    for teste, resultado in resultados.items():
        if resultado is True:
            status = "✅ PASSOU"
        elif resultado is False:
            status = "❌ FALHOU"
        else:
            status = "⚠️ N/A"
        print(f"   {teste.upper()}: {status}")
    
    if all(r for r in resultados.values() if r is not None):
        print("\n✅ Todos os testes passaram! O banco de dados está configurado corretamente.")
        return 0
    else:
        print("\n❌ Alguns testes falharam. Verifique os erros acima.")
        print("\n📚 PRÓXIMOS PASSOS:")
        print("   1. Verifique as variáveis de ambiente no Cloud Run")
        print("   2. Confirme que --add-cloudsql-instances foi usado no deploy")
        print("   3. Verifique permissões IAM (Cloud SQL Client role)")
        print("   4. Confirme que o Cloud SQL instance está rodando")
        return 1

if __name__ == '__main__':
    sys.exit(main())


