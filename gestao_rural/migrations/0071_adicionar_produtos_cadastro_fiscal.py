# Generated manually for cadastro de produtos sincronizado com Receita Federal
# VERSÃO CORRIGIDA: Campo NCM permite NULL inicialmente para evitar erro 500

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestao_rural', '0070_adicionar_cliente_nota_fiscal'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaProduto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True, verbose_name='Nome da Categoria')),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
            ],
            options={
                'verbose_name': 'Categoria de Produto',
                'verbose_name_plural': 'Categorias de Produtos',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(help_text='Código interno do produto', max_length=50, unique=True, verbose_name='Código do Produto')),
                ('descricao', models.CharField(max_length=200, verbose_name='Descrição do Produto')),
                ('descricao_completa', models.TextField(blank=True, help_text='Descrição detalhada do produto', null=True, verbose_name='Descrição Completa')),
                ('unidade_medida', models.CharField(choices=[('UN', 'Unidade'), ('KG', 'Quilograma'), ('TON', 'Tonelada'), ('L', 'Litro'), ('M', 'Metro'), ('M2', 'Metro Quadrado'), ('M3', 'Metro Cúbico'), ('SC', 'Saca'), ('CX', 'Caixa'), ('PC', 'Peça'), ('FD', 'Fardo'), ('RL', 'Rolo')], default='UN', max_length=10, verbose_name='Unidade de Medida')),
                # CORREÇÃO: NCM permite NULL inicialmente (será tratado na 0072)
                ('ncm', models.CharField(blank=True, help_text='Nomenclatura Comum do Mercosul (ex: 0102.29.00)', max_length=10, null=True, verbose_name='NCM')),
                ('ncm_descricao', models.CharField(blank=True, help_text='Descrição oficial do NCM pela Receita', max_length=500, null=True, verbose_name='Descrição do NCM')),
                ('ncm_validado', models.BooleanField(default=False, help_text='Indica se o NCM foi validado com a Receita Federal', verbose_name='NCM Validado')),
                ('ncm_data_validacao', models.DateTimeField(blank=True, null=True, verbose_name='Data de Validação do NCM')),
                ('cfop_entrada', models.CharField(blank=True, help_text='CFOP padrão para compras (ex: 1102)', max_length=10, null=True, verbose_name='CFOP Entrada')),
                ('cfop_saida_estadual', models.CharField(blank=True, help_text='CFOP padrão para vendas dentro do estado (ex: 5102)', max_length=10, null=True, verbose_name='CFOP Saída Estadual')),
                ('cfop_saida_interestadual', models.CharField(blank=True, help_text='CFOP padrão para vendas fora do estado (ex: 6102)', max_length=10, null=True, verbose_name='CFOP Saída Interestadual')),
                ('cst_icms', models.CharField(blank=True, help_text='Código de Situação Tributária do ICMS', max_length=3, null=True, verbose_name='CST ICMS')),
                ('aliquota_icms', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='Alíquota ICMS (%)')),
                ('cst_ipi', models.CharField(blank=True, help_text='Código de Situação Tributária do IPI', max_length=3, null=True, verbose_name='CST IPI')),
                ('aliquota_ipi', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='Alíquota IPI (%)')),
                ('cst_pis', models.CharField(blank=True, help_text='Código de Situação Tributária do PIS', max_length=3, null=True, verbose_name='CST PIS')),
                ('aliquota_pis', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='Alíquota PIS (%)')),
                ('cst_cofins', models.CharField(blank=True, help_text='Código de Situação Tributária do COFINS', max_length=3, null=True, verbose_name='CST COFINS')),
                ('aliquota_cofins', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='Alíquota COFINS (%)')),
                ('preco_venda', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='Preço de Venda (R$)')),
                ('preco_custo', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='Preço de Custo (R$)')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('sincronizado_receita', models.BooleanField(default=False, help_text='Indica se os dados foram sincronizados com a Receita Federal', verbose_name='Sincronizado com Receita')),
                ('data_sincronizacao', models.DateTimeField(blank=True, null=True, verbose_name='Data da Última Sincronização')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='produtos', to='gestao_rural.categoriaproduto', verbose_name='Categoria')),
                ('usuario_cadastro', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='produtos_cadastrados', to=settings.AUTH_USER_MODEL, verbose_name='Usuário que Cadastrou')),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
                'ordering': ['categoria', 'descricao'],
            },
        ),
        migrations.AddIndex(
            model_name='produto',
            index=models.Index(fields=['codigo'], name='gestao_rural_codigo_idx'),
        ),
        migrations.AddIndex(
            model_name='produto',
            index=models.Index(fields=['ncm'], name='gestao_rural_ncm_idx'),
        ),
        migrations.AddIndex(
            model_name='produto',
            index=models.Index(fields=['ativo'], name='gestao_rural_ativo_idx'),
        ),
        migrations.AddField(
            model_name='itemnotafiscal',
            name='produto',
            field=models.ForeignKey(blank=True, help_text='Produto cadastrado (preenche automaticamente os dados fiscais)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='itens_nota_fiscal', to='gestao_rural.produto', verbose_name='Produto'),
        ),
    ]
