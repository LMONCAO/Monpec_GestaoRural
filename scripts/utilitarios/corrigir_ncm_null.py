#!/usr/bin/env python
"""
Script para corrigir valores NULL no campo NCM antes de aplicar migração 0072
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.db import connection

print("=" * 60)
print("CORRIGINDO VALORES NULL NO CAMPO NCM")
print("=" * 60)
print()

try:
    with connection.cursor() as cursor:
        # Verificar se tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'gestao_rural_produto'
            )
        """)
        tabela_existe = cursor.fetchone()[0]
        
        if not tabela_existe:
            print("⚠️ Tabela gestao_rural_produto não existe ainda.")
            print("   Isso é normal se a migração 0071 ainda não foi aplicada.")
            sys.exit(0)
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM gestao_rural_produto")
        total = cursor.fetchone()[0]
        print(f"📊 Total de registros na tabela: {total}")
        
        # Contar registros com NCM NULL ou vazio
        cursor.execute("""
            SELECT COUNT(*) FROM gestao_rural_produto 
            WHERE ncm IS NULL OR ncm = ''
        """)
        null_count = cursor.fetchone()[0]
        print(f"⚠️ Registros com NCM NULL ou vazio: {null_count}")
        
        if null_count > 0:
            print()
            print("▶ Corrigindo valores NULL...")
            cursor.execute("""
                UPDATE gestao_rural_produto 
                SET ncm = '0000.00.00' 
                WHERE ncm IS NULL OR ncm = ''
            """)
            print(f"✅ {null_count} registro(s) corrigido(s)!")
        else:
            print("✅ Nenhum registro com NCM NULL encontrado.")
        
        print()
        print("=" * 60)
        print("✅ CORREÇÃO CONCLUÍDA!")
        print("=" * 60)
        print()
        print("Agora você pode aplicar a migração 0072 com segurança.")
        print()

except Exception as e:
    print(f'❌ ERRO: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)







