#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

def verificar_tabelas():
    """Verifica se as tabelas relacionadas a assinaturas existem"""
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name LIKE 'gestao_rural_%'
                ORDER BY table_name
            """)
        else:  # SQLite
            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name LIKE 'gestao_rural_%'
                ORDER BY name
            """)

        tables = cursor.fetchall()

        print("Tabelas gestao_rural encontradas:")
        assinaturas_related = []
        for table in tables:
            table_name = table[0]
            print(f"- {table_name}")
            if 'assinaturacliente' in table_name.lower() or 'assinatura' in table_name.lower():
                assinaturas_related.append(table_name)

        print(f"\nTotal de tabelas: {len(tables)}")

        if assinaturas_related:
            print("
Tabelas relacionadas a assinaturas encontradas:")
            for table in assinaturas_related:
                print(f"- {table}")
        else:
            print("
NENHUMA tabela de assinatura encontrada!")

        # Verificar especificamente a tabela assinaturacliente
        print(f"\nVerificando tabela 'gestao_rural_assinaturacliente':")
        if connection.vendor == 'postgresql':
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'gestao_rural_assinaturacliente'
                );
            """)
        else:
            cursor.execute("""
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type='table'
                AND name = 'gestao_rural_assinaturacliente'
            """)        exists = cursor.fetchone()[0]
        if exists:
            print("Tabela 'gestao_rural_assinaturacliente' EXISTE")            # Verificar estrutura da tabela
            print("\nEstrutura da tabela:")
            if connection.vendor == 'postgresql':
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = 'gestao_rural_assinaturacliente'
                    ORDER BY ordinal_position
                """)
            else:
                cursor.execute("PRAGMA table_info(gestao_rural_assinaturacliente)")            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if len(col) > 2 and col[2] else 'NOT NULL'}")
        else:
            print("Tabela 'gestao_rural_assinaturacliente' NAO EXISTE")if __name__ == '__main__':
    verificar_tabelas()