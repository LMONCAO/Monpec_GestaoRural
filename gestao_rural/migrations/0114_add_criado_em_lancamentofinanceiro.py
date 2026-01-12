# Migration para adicionar coluna criado_em à tabela LancamentoFinanceiro

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0113_force_create_tables'),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Adicionar coluna criado_em se ela não existir
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'gestao_rural_lancamentofinanceiro'
                    AND column_name = 'criado_em'
                ) THEN
                    ALTER TABLE gestao_rural_lancamentofinanceiro
                    ADD COLUMN criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                END IF;
            END $$;

            -- Preencher valores existentes
            UPDATE gestao_rural_lancamentofinanceiro
            SET criado_em = NOW()
            WHERE criado_em IS NULL;
            """,
            reverse_sql="""
            -- Remover coluna criado_em
            ALTER TABLE gestao_rural_lancamentofinanceiro DROP COLUMN IF EXISTS criado_em;
            """
        ),
    ]