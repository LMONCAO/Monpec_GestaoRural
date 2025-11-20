import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / 'db.sqlite3'

conn = sqlite3.connect(db_path)

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'gestao_rural%';"
).fetchall()

print('Tabelas encontradas:', tables)

last_migrations = conn.execute(
    "SELECT app, name FROM django_migrations ORDER BY applied DESC LIMIT 10;"
).fetchall()

print('Últimas migrations aplicadas:', last_migrations)


