"""
Script para criar a tabela VerificacaoEmail manualmente
Uso: python311\python.exe criar_tabela_verificacao_email.py
"""
import os
import sys
import django

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

print("=" * 60)
print("CRIANDO TABELA VERIFICACAO EMAIL")
print("=" * 60)
print()

# SQL para criar a tabela
sql = """
CREATE TABLE IF NOT EXISTS gestao_rural_verificacaoemail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token VARCHAR(64) NOT NULL UNIQUE,
    email_verificado BOOLEAN NOT NULL DEFAULT 0,
    token_expira_em DATETIME NOT NULL,
    tentativas_verificacao INTEGER UNSIGNED NOT NULL DEFAULT 0,
    criado_em DATETIME NOT NULL,
    verificado_em DATETIME NULL,
    usuario_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (usuario_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
"""

try:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        print("[OK] Tabela gestao_rural_verificacaoemail criada com sucesso!")
        print()
        print("Agora voce pode fazer login normalmente.")
except Exception as e:
    print(f"[ERRO] Nao foi possivel criar a tabela: {e}")
    print()
    print("Tentando verificar se a tabela ja existe...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gestao_rural_verificacaoemail';")
            result = cursor.fetchone()
            if result:
                print("[OK] A tabela ja existe!")
            else:
                print("[ERRO] A tabela nao existe e nao foi possivel criar.")
    except Exception as e2:
        print(f"[ERRO] Erro ao verificar: {e2}")


