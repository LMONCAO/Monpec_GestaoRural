from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0032_compras_portal_fornecedores'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicadorplanejado',
            name='codigo',
            field=models.CharField(
                blank=True,
                help_text=(
                    "Identificador para cálculo automático (ex: TAXA_PRENHEZ, "
                    "ARROBAS_VENDIDAS, CUSTO_ARROBA)."
                ),
                max_length=60,
                verbose_name='Código do indicador',
            ),
        ),
        migrations.AddField(
            model_name='indicadorplanejado',
            name='direcao_meta',
            field=models.CharField(
                choices=[
                    ('MAIOR', 'Maior é melhor'),
                    ('MENOR', 'Menor é melhor'),
                    ('ALVO', 'Alcançar valor específico'),
                ],
                default='MAIOR',
                max_length=10,
                verbose_name='Direção desejada',
            ),
        ),
        migrations.AddField(
            model_name='indicadorplanejado',
            name='eixo_estrategico',
            field=models.CharField(
                choices=[
                    ('REPRODUCAO', 'Reprodução'),
                    ('ENGORDA', 'Engorda'),
                    ('FINANCEIRO', 'Financeiro'),
                    ('SANIDADE', 'Sanidade'),
                    ('OPERACIONAL', 'Operacional'),
                    ('SUSTENTABILIDADE', 'Sustentabilidade'),
                ],
                default='OPERACIONAL',
                max_length=20,
                verbose_name='Eixo estratégico',
            ),
        ),
        migrations.AddField(
            model_name='indicadorplanejado',
            name='valor_base',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Valor de referência já alcançado, útil para comparar evolução.',
                max_digits=12,
                null=True,
                verbose_name='Valor base (realizado atual)',
            ),
        ),
    ]

