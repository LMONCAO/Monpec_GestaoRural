# Generated migration for adicionar campos obrigatórios NF-e ao modelo Produto
# VERSÃO CORRIGIDA: Preenche valores NULL antes de tornar campo obrigatório

from django.db import migrations, models


def preencher_ncm_vazio(apps, schema_editor):
    """
    Preenche NCM vazio/NULL com valor padrão antes de tornar obrigatório.
    Isso evita erro 500 quando há produtos existentes sem NCM.
    """
    Produto = apps.get_model('gestao_rural', 'Produto')
    db_alias = schema_editor.connection.alias
    
    # Preencher produtos sem NCM com valor padrão genérico
    # O usuário deve atualizar depois com o NCM correto
    produtos_sem_ncm = Produto.objects.using(db_alias).filter(
        ncm__isnull=True
    ) | Produto.objects.using(db_alias).filter(
        ncm=''
    )
    
    count = produtos_sem_ncm.update(ncm='0000.00.00')
    
    if count > 0:
        print(f'⚠️ ATENÇÃO: {count} produto(s) tiveram NCM preenchido com valor genérico "0000.00.00".')
        print('   Por favor, atualize o NCM correto desses produtos.')


def desfazer_preenchimento(apps, schema_editor):
    """Função reversa - não faz nada pois não podemos reverter para NULL"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0071_adicionar_produtos_cadastro_fiscal'),
    ]

    operations = [
        # 1. PRIMEIRO: Preencher valores NULL/vazios com valor padrão
        migrations.RunPython(preencher_ncm_vazio, desfazer_preenchimento),
        
        # 2. DEPOIS: Tornar NCM obrigatório (agora seguro, pois não há NULLs)
        migrations.AlterField(
            model_name='produto',
            name='ncm',
            field=models.CharField(
                help_text='Nomenclatura Comum do Mercosul (ex: 0102.29.00) - OBRIGATÓRIO',
                max_length=10,
                verbose_name='NCM',
                blank=False,
                null=False
            ),
        ),
        
        # 3. Adicionar campo origem_mercadoria (OBRIGATÓRIO na NF-e)
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
        
        # 4. Adicionar campo CEST (opcional mas importante)
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
        
        # 5. Adicionar campo GTIN/EAN (código de barras)
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
        
        # 6. Adicionar campo Ex_TIPI
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
