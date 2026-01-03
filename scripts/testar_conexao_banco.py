#!/usr/bin/env python
"""
Script simples para testar conexão com banco de dados
Útil para verificar antes de fazer deploy
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

from django.db import connection

def main():
    """Testa a conexão com o banco de dados"""
    print("🔍 Testando conexão com banco de dados...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Conexão bem-sucedida!")
            print(f"   PostgreSQL: {version[0][:60]}...")
            
            # Testar query simples
            cursor.execute("SELECT current_database(), current_user;")
            db_info = cursor.fetchone()
            print(f"   Database: {db_info[0]}")
            print(f"   Usuário: {db_info[1]}")
            
            return 0
    except Exception as e:
        print(f"❌ ERRO ao conectar ao banco de dados!")
        print(f"   {type(e).__name__}: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())


