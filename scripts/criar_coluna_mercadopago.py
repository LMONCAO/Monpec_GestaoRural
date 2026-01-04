#!/usr/bin/env python
"""
Script para criar a coluna mercadopago_customer_id na tabela AssinaturaCliente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.db import connection

c = connection.cursor()

# Verificar se coluna existe
c.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='gestao_rural_assinaturacliente' 
    AND column_name='mercadopago_customer_id'
""")
r = c.fetchone()

if r:
    print('✅ Coluna mercadopago_customer_id JÁ EXISTE')
else:
    print('❌ Coluna mercadopago_customer_id NÃO EXISTE - Criando...')
    try:
        c.execute("""
            ALTER TABLE gestao_rural_assinaturacliente 
            ADD COLUMN mercadopago_customer_id VARCHAR(255) NULL
        """)
        c.execute("""
            CREATE INDEX IF NOT EXISTS gestao_rura_mercado_1a0de9_idx 
            ON gestao_rural_assinaturacliente(mercadopago_customer_id)
        """)
        print('✅ Coluna mercadopago_customer_id CRIADA COM SUCESSO')
    except Exception as e:
        print(f'❌ ERRO ao criar coluna: {e}')


