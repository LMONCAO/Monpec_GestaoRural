#!/usr/bin/env python
"""
Script simples para corrigir a coluna criado_em
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

import django
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    print("Verificando coluna criado_em...")

    # Verificar se existe
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'gestao_rural_lancamentofinanceiro' AND column_name = 'criado_em';")

    if cursor.fetchone():
        print("✅ Coluna criado_em já existe!")
    else:
        print("Adicionando coluna criado_em...")
        cursor.execute("ALTER TABLE gestao_rural_lancamentofinanceiro ADD COLUMN criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();")
        print("✅ Coluna criada!")

print("Correção concluída!")