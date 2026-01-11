# Migração de sincronização para resolver problema da migração 0034
# Esta migração verifica se as tabelas da migração 0034 já existem
# e marca a migração 0034 como aplicada se necessário

from django.db import migrations, connection


def verificar_e_sincronizar_0034(apps, schema_editor):
    """
    Verifica se as tabelas da migração 0034 já existem no banco.
    Se existirem, marca a migração 0034 como aplicada.
    """
    with connection.cursor() as cursor:
        # Verificar se tabelas principais da migração 0034 existem
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'gestao_rural_contafinanceira',
                'gestao_rural_categoriafinanceira',
                'gestao_rural_lancamentofinanceiro',
                'gestao_rural_centrocustofinanceiro'
            );
        """)
        tabelas_existentes = [row[0] for row in cursor.fetchall()]
        
        # Se todas as tabelas principais existem, marcar migração 0034 como aplicada
        tabelas_esperadas = [
            'gestao_rural_contafinanceira',
            'gestao_rural_categoriafinanceira',
            'gestao_rural_lancamentofinanceiro',
        ]
        
        todas_existem = all(tabela in tabelas_existentes for tabela in tabelas_esperadas)
        
        if todas_existem:
            # Verificar se migração 0034 já está marcada como aplicada
            cursor.execute("""
                SELECT COUNT(*) 
                FROM django_migrations 
                WHERE app = 'gestao_rural' 
                AND name = '0034_financeiro_reestruturado';
            """)
            ja_aplicada = cursor.fetchone()[0] > 0
            
            if not ja_aplicada:
                # Marcar migração 0034 como aplicada
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied)
                    VALUES ('gestao_rural', '0034_financeiro_reestruturado', NOW());
                """)
                print("✅ Migração 0034 marcada como aplicada (tabelas já existiam)")


def reverse_sincronizar_0034(apps, schema_editor):
    """Função reversa - não faz nada pois não podemos desfazer isso com segurança"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0104_remover_stripe_do_modelo'),
    ]

    operations = [
        migrations.RunPython(
            verificar_e_sincronizar_0034,
            reverse_sincronizar_0034,
        ),
    ]

