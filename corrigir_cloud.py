#!/usr/bin/env python
"""
Script para corrigir a coluna criado_em no ambiente Google Cloud
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')

import django
django.setup()

from django.db import connection

def corrigir_coluna_cloud():
    """Corrige a coluna criado_em no ambiente do Google Cloud"""
    with connection.cursor() as cursor:
        try:
            print("Verificando coluna criado_em no Google Cloud...")

            # Verificar se a coluna existe
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'gestao_rural_lancamentofinanceiro'
                AND column_name = 'criado_em';
            """)

            coluna_existe = cursor.fetchone()

            if coluna_existe:
                print("Coluna criado_em ja existe no Google Cloud!")
                return True

            print("Coluna criado_em nao encontrada. Adicionando...")

            # Adicionar a coluna
            cursor.execute("""
                ALTER TABLE gestao_rural_lancamentofinanceiro
                ADD COLUMN criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            """)

            # Verificar se foi adicionada
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'gestao_rural_lancamentofinanceiro'
                AND column_name = 'criado_em';
            """)

            if cursor.fetchone():
                print("Coluna criado_em adicionada com sucesso no Google Cloud!")

                # Preencher valores existentes
                cursor.execute("""
                    UPDATE gestao_rural_lancamentofinanceiro
                    SET criado_em = NOW()
                    WHERE criado_em IS NULL;
                """)

                print("Valores preenchidos para registros existentes no Google Cloud!")
                return True
            else:
                print("Erro: Coluna nao foi criada no Google Cloud!")
                return False

        except Exception as e:
            print(f"Erro ao corrigir coluna no Google Cloud: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("Iniciando correcao da coluna criado_em no Google Cloud...")
    sucesso = corrigir_coluna_cloud()

    if sucesso:
        print("\nCorrecao concluida no Google Cloud! O erro deve estar resolvido.")
    else:
        print("\nFalha na correcao no Google Cloud.")