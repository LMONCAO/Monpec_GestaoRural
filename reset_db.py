import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        user='postgres',
        password='postgres',
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Terminar conexões ativas no banco
    cursor.execute("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = 'monpec_db_local' AND pid <> pg_backend_pid();
    """)

    # Dropar e recriar banco
    cursor.execute('DROP DATABASE IF EXISTS monpec_db_local')
    cursor.execute('CREATE DATABASE monpec_db_local')
    print('Banco monpec_db_local recriado!')

    cursor.close()
    conn.close()
except Exception as e:
    print('Erro: ' + str(e))





