import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    # Conectar ao banco postgres padrão
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        user='postgres',
        password='L6171r12@@jjms',
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()

    # Terminar conexões ativas no banco que vamos criar
    cursor.execute("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = 'monpec_oficial' AND pid <> pg_backend_pid();
    """)

    # Dropar e recriar banco
    cursor.execute('DROP DATABASE IF EXISTS monpec_oficial')
    cursor.execute('CREATE DATABASE monpec_oficial')

    print('Banco monpec_oficial criado com sucesso!')

    cursor.close()
    conn.close()

except Exception as e:
    print(f'Erro: {str(e)}')