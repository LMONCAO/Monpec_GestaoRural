#!/usr/bin/env python
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.append('.')
django.setup()

from django.db import connection

cursor = connection.cursor()

print("=== MIGRAÇÕES DO APP gestao_rural ===")
cursor.execute("SELECT * FROM django_migrations WHERE app='gestao_rural' ORDER BY id")
migrations = cursor.fetchall()
for mig in migrations:
    print(f'{mig[0]}: {mig[1]} - {mig[2]}')

print("\n=== VERIFICANDO DEPENDÊNCIAS ===")
# Verificar se a migração 0006 existe
cursor.execute("SELECT * FROM django_migrations WHERE app='gestao_rural' AND name LIKE '%0006%'")
result = cursor.fetchone()
if result:
    print('✅ Migração 0006 encontrada')
else:
    print('❌ Migração 0006 NÃO encontrada - problema!')

# Verificar se 0035 depende de 0006
cursor.execute("SELECT * FROM django_migrations WHERE app='gestao_rural' AND name LIKE '%0035%'")
result_35 = cursor.fetchone()
if result_35:
    print('✅ Migração 0035 encontrada')
else:
    print('❌ Migração 0035 não encontrada')