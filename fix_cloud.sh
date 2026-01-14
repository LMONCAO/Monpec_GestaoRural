#!/bin/bash
# Comando para executar no Google Cloud via SSH

echo "Executando correcao da coluna criado_em no Google Cloud..."

python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
import django
django.setup()
from django.db import connection

with connection.cursor() as cursor:
    print('Verificando coluna criado_em...')
    cursor.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name = 'gestao_rural_lancamentofinanceiro' AND column_name = 'criado_em';\")
    if cursor.fetchone():
        print('Coluna ja existe!')
    else:
        print('Adicionando coluna...')
        cursor.execute('ALTER TABLE gestao_rural_lancamentofinanceiro ADD COLUMN criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();')
        cursor.execute('UPDATE gestao_rural_lancamentofinanceiro SET criado_em = NOW() WHERE criado_em IS NULL;')
        print('Coluna criada e valores preenchidos!')

print('Correcao concluida!')
"