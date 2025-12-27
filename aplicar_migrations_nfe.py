#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para aplicar migrations de NF-e
Resolve o erro: no such column: gestao_rural_notafiscal.cliente_id
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def main():
    print("=" * 60)
    print("Aplicando Migrations de NF-e")
    print("=" * 60)
    print()
    
    # Verificar migrations pendentes
    print("Verificando migrations pendentes...")
    print()
    
    try:
        # Aplicar todas as migrations pendentes
        print("Aplicando migrations do app gestao_rural...")
        call_command('migrate', 'gestao_rural', verbosity=2, interactive=False)
        
        print()
        print("=" * 60)
        print("✅ Migrations aplicadas com sucesso!")
        print("=" * 60)
        print()
        
        # Verificar se a coluna cliente_id existe agora
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(gestao_rural_notafiscal)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'cliente_id' in columns:
                print("✅ Coluna 'cliente_id' encontrada na tabela gestao_rural_notafiscal")
            else:
                print("⚠️  Coluna 'cliente_id' ainda não encontrada")
                print("   Pode ser necessário aplicar migrations manualmente:")
                print("   python manage.py migrate gestao_rural")
        
        print()
        print("Próximos passos:")
        print("1. Reinicie o servidor Django")
        print("2. Acesse o sistema novamente")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Erro ao aplicar migrations:")
        print("=" * 60)
        print(str(e))
        print()
        print("Tente executar manualmente:")
        print("  python manage.py migrate gestao_rural")
        print()
        sys.exit(1)

if __name__ == '__main__':
    main()






































