#!/usr/bin/env python
import os
import sqlite3
import time

# Caminho para o banco de dados
db_path = 'db.sqlite3'

print("Verificando banco de dados...")

# Verificar se o arquivo existe
if not os.path.exists(db_path):
    print("Banco de dados não encontrado!")
    exit(1)

try:
    # Tentar conectar e executar uma operação simples
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()
    
    # Verificar se o banco está bloqueado
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tabelas encontradas: {len(tables)}")
    
    # Executar PRAGMA para desbloquear
    cursor.execute("PRAGMA busy_timeout = 30000;")  # 30 segundos
    cursor.execute("PRAGMA journal_mode = WAL;")    # Modo WAL para melhor concorrência
    
    conn.commit()
    conn.close()
    
    print("Banco de dados desbloqueado com sucesso!")
    
except sqlite3.OperationalError as e:
    print(f"Erro ao acessar banco: {e}")
    print("Tentando forçar desbloqueio...")
    
    # Tentar remover arquivos de lock se existirem
    lock_files = [db_path + '-wal', db_path + '-shm', db_path + '-journal']
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            try:
                os.remove(lock_file)
                print(f"Removido: {lock_file}")
            except:
                print(f"Não foi possível remover: {lock_file}")
    
    print("Tentando reconectar...")
    time.sleep(2)
    
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        conn.close()
        print("Banco de dados desbloqueado!")
    except Exception as e2:
        print(f"Ainda com problemas: {e2}")

except Exception as e:
    print(f"Erro inesperado: {e}")

print("Processo concluído.")



