#!/usr/bin/env python
"""
Script para corrigir a coluna criado_em diretamente no PostgreSQL remoto
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def corrigir_coluna():
    """Conecta ao PostgreSQL remoto e corrige a coluna"""
    try:
        print("Conectando ao banco PostgreSQL...")

        # Configurações do banco (ajuste conforme necessário)
        conn = psycopg2.connect(
            host='34.9.51.178',  # IP do seu servidor PostgreSQL
            port='5432',
            user='postgres',
            password='L6171r12@@jjms',
            database='monpec-db'  # Nome do banco
        )

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("Verificando se a coluna criado_em existe...")

        # Verificar se a coluna existe
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'gestao_rural_lancamentofinanceiro'
            AND column_name = 'criado_em';
        """)

        coluna_existe = cursor.fetchone()

        if coluna_existe:
            print("A coluna criado_em ja existe!")
            cursor.close()
            conn.close()
            return True

        print("Coluna criado_em nao encontrada. Adicionando...")

        # Adicionar a coluna
        cursor.execute("""
            ALTER TABLE gestao_rural_lancamentofinanceiro
            ADD COLUMN criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();
        """)

        print("Coluna criado_em adicionada!")

        # Verificar se foi criada
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'gestao_rural_lancamentofinanceiro'
            AND column_name = 'criado_em';
        """)

        if cursor.fetchone():
            print("Verificacao: Coluna criada com sucesso!")

            # Preencher valores existentes
            cursor.execute("""
                UPDATE gestao_rural_lancamentofinanceiro
                SET criado_em = NOW()
                WHERE criado_em IS NULL;
            """)

            print("Valores preenchidos para registros existentes!")
        else:
            print("Erro: Coluna nao foi criada!")

        cursor.close()
        conn.close()

        print("\nCorrecao concluida! O erro deve estar resolvido.")
        return True

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Iniciando correcao da coluna criado_em no PostgreSQL...")
    corrigir_coluna()