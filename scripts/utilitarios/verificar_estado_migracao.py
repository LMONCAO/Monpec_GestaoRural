#!/usr/bin/env python
"""
Script para verificar estado da migração 0071 e tabela gestao_rural_produto
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Verificar se migração 0071 está registrada
cursor.execute(
    "SELECT COUNT(*) FROM django_migrations WHERE app='gestao_rural' AND name='0071_adicionar_produtos_cadastro_fiscal';"
)
mig_count = cursor.fetchone()[0]

# Verificar se tabela existe
cursor.execute(
    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_produto');"
)
table_exists = cursor.fetchone()[0]

print(f'Migração 0071 registrada: {mig_count > 0}')
print(f'Tabela gestao_rural_produto existe: {table_exists}')

if mig_count > 0 and not table_exists:
    print('⚠️ PROBLEMA: Migração registrada mas tabela não existe!')
    sys.exit(1)
elif mig_count == 0 and not table_exists:
    print('ℹ️ Migração 0071 ainda não foi aplicada.')
    sys.exit(0)
else:
    print('✅ Tudo OK!')
    sys.exit(0)








