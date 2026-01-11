import sqlite3

try:
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(gestao_rural_produtorrural);")
    cols = cursor.fetchall()
    print('Colunas da tabela produtorrural:')
    for col in cols:
        print(f'  {col[1]}')
    conn.close()
except Exception as e:
    print(f'Erro: {e}')




