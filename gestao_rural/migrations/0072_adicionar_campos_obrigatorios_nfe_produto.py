# Generated migration for adicionar campos obrigatórios NF-e ao modelo Produto

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0071_adicionar_produtos_cadastro_fiscal'),
    ]

    operations = [
        # Tornar NCM obrigatório (alterar campo existente)
        migrations.AlterField(
            model_name='produto',
            name='ncm',
            field=models.CharField(
                help_text='Nomenclatura Comum do Mercosul (ex: 0102.29.00) - OBRIGATÓRIO',
                max_length=10,
                verbose_name='NCM'
            ),
        ),
        # Adicionar campo origem_mercadoria (OBRIGATÓRIO na NF-e)
        migrations.AddField(
            model_name='produto',
            name='origem_mercadoria',
            field=models.CharField(
                choices=[
                    ('0', '0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8'),
                    ('1', '1 - Estrangeira - Importação direta, exceto a indicada no código 6'),
                    ('2', '2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7'),
                    ('3', '3 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 40%'),
                    ('4', '4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos'),
                    ('5', '5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%'),
                    ('6', '6 - Estrangeira - Importação direta, sem similar nacional'),
                    ('7', '7 - Estrangeira - Adquirida no mercado interno, sem similar nacional'),
                    ('8', '8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%'),
                ],
                default='0',
                help_text='Origem da mercadoria conforme tabela da Receita Federal - OBRIGATÓRIO na NF-e',
                max_length=1,
                verbose_name='Origem da Mercadoria'
            ),
        ),
        # Adicionar campo CEST (opcional mas importante)
        migrations.AddField(
            model_name='produto',
            name='cest',
            field=models.CharField(
                blank=True,
                help_text='Código Especificador da Substituição Tributária (7 dígitos) - Obrigatório para alguns produtos',
                max_length=7,
                null=True,
                verbose_name='CEST'
            ),
        ),
        # Adicionar campo GTIN/EAN (código de barras)
        migrations.AddField(
            model_name='produto',
            name='gtin',
            field=models.CharField(
                blank=True,
                help_text='Código GTIN (EAN/UPC) do produto (código de barras)',
                max_length=14,
                null=True,
                verbose_name='GTIN/EAN'
            ),
        ),
        # Adicionar campo Ex_TIPI
        migrations.AddField(
            model_name='produto',
            name='ex_tipi',
            field=models.CharField(
                blank=True,
                help_text='Código de exceção da TIPI (quando aplicável)',
                max_length=3,
                null=True,
                verbose_name='Exceção da TIPI'
            ),
        ),
    ]




















