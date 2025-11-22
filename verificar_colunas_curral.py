"""
Script para verificar colunas da tabela CurralSessao
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute('PRAGMA table_info(gestao_rural_curralsessao);')
cols = [c[1] for c in cursor.fetchall()]

print('Colunas na tabela gestao_rural_curralsessao:')
for col in sorted(cols):
    print(f'  [OK] {col}')

# Verificar se todas as colunas necessárias existem
colunas_necessarias = ['tipo_trabalho', 'nome_lote', 'pasto_origem', 'quantidade_esperada']
print()
print('Verificacao:')
for col in colunas_necessarias:
    if col in cols:
        print(f'  [OK] {col} - Existe')
    else:
        print(f'  [ERRO] {col} - FALTANDO')

