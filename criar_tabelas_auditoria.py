"""
Script para criar as tabelas de auditoria manualmente
Uso: python311\python.exe criar_tabelas_auditoria.py
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
print("CRIANDO TABELAS DE AUDITORIA")
print("=" * 60)
print()

# SQL para criar a tabela SessaoSegura
sql_sessao = """
CREATE TABLE IF NOT EXISTS gestao_rural_sessaosegura (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key VARCHAR(40) NOT NULL UNIQUE,
    ip_address VARCHAR(39) NOT NULL,
    user_agent TEXT NOT NULL,
    ultima_atividade DATETIME NOT NULL,
    criado_em DATETIME NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT 1,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
"""

# SQL para criar índices
sql_indices = """
CREATE INDEX IF NOT EXISTS gestao_rural_sessaosegura_usuario_id_ultima_atividade_idx 
    ON gestao_rural_sessaosegura(usuario_id, ultima_atividade DESC);
    
CREATE INDEX IF NOT EXISTS gestao_rural_sessaosegura_ip_address_ultima_atividade_idx 
    ON gestao_rural_sessaosegura(ip_address, ultima_atividade DESC);
"""

# SQL para criar a tabela LogAuditoria (caso não exista)
sql_log = """
CREATE TABLE IF NOT EXISTS gestao_rural_logauditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_acao VARCHAR(50) NOT NULL,
    descricao TEXT NOT NULL,
    usuario_id INTEGER NULL,
    ip_address VARCHAR(39) NULL,
    user_agent TEXT NOT NULL,
    nivel_severidade VARCHAR(20) NOT NULL,
    sucesso BOOLEAN NOT NULL DEFAULT 1,
    erro TEXT NULL,
    criado_em DATETIME NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES auth_user(id) ON DELETE SET NULL
);
"""

tabelas_criadas = []

try:
    with connection.cursor() as cursor:
        # Criar tabela SessaoSegura
        cursor.execute(sql_sessao)
        tabelas_criadas.append("gestao_rural_sessaosegura")
        print("[OK] Tabela gestao_rural_sessaosegura criada!")
        
        # Criar índices separadamente
        for index_sql in sql_indices.strip().split(';'):
            if index_sql.strip():
                try:
                    cursor.execute(index_sql.strip() + ';')
                except Exception as e:
                    print(f"[AVISO] Erro ao criar indice (pode ja existir): {e}")
        print("[OK] Indices da tabela gestao_rural_sessaosegura verificados!")
        
        # Criar tabela LogAuditoria (caso não exista)
        cursor.execute(sql_log)
        tabelas_criadas.append("gestao_rural_logauditoria")
        print("[OK] Tabela gestao_rural_logauditoria verificada/criada!")
        
except Exception as e:
    print(f"[ERRO] Nao foi possivel criar as tabelas: {e}")
    print()
    print("Verificando tabelas existentes...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'gestao_rural_%';")
            tabelas = cursor.fetchall()
            print(f"[INFO] Tabelas encontradas: {[t[0] for t in tabelas]}")
    except Exception as e2:
        print(f"[ERRO] Erro ao verificar: {e2}")

print()
print("=" * 60)
if tabelas_criadas:
    print("[SUCESSO] Tabelas criadas com sucesso!")
    print("Agora voce pode fazer login normalmente.")
else:
    print("[AVISO] Nenhuma tabela foi criada.")
print("=" * 60)

