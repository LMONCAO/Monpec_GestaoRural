from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import gestao_rural.models_financeiro


def create_default_widgets(apps, schema_editor):
    Widget = apps.get_model('gestao_rural', 'FinanceiroWidgetCatalogo')
    widgets = [
        {
            'chave': 'kpi_receita',
            'titulo': 'Receita Mensal',
            'descricao': 'Indicador consolidado das receitas do período selecionado.',
            'categoria': 'KPI',
            'icone': 'bi-arrow-up-circle',
            'tamanho_padrao': 'sm',
            'ordem_padrao': 1,
        },
        {
            'chave': 'kpi_despesa',
            'titulo': 'Despesas Mensais',
            'descricao': 'Indicador consolidado das despesas do período selecionado.',
            'categoria': 'KPI',
            'icone': 'bi-arrow-down-circle',
            'tamanho_padrao': 'sm',
            'ordem_padrao': 2,
        },
        {
            'chave': 'kpi_saldo',
            'titulo': 'Saldo Projetado',
            'descricao': 'Resultado líquido projetado com base nas entradas e saídas futuras.',
            'categoria': 'KPI',
            'icone': 'bi-wallet-fill',
            'tamanho_padrao': 'sm',
            'ordem_padrao': 3,
        },
        {
            'chave': 'kpi_lucro',
            'titulo': 'Lucro Líquido',
            'descricao': 'Lucro líquido consolidado do período.',
            'categoria': 'KPI',
            'icone': 'bi-trophy-fill',
            'tamanho_padrao': 'sm',
            'ordem_padrao': 4,
        },
        {
            'chave': 'grafico_fluxo_caixa',
            'titulo': 'Fluxo de Caixa Projetado',
            'descricao': 'Evolução do fluxo de caixa ao longo do período selecionado.',
            'categoria': 'GRAFICO',
            'icone': 'bi-graph-up',
            'tamanho_padrao': 'lg',
            'ordem_padrao': 5,
        },
        {
            'chave': 'grafico_receitas_despesas',
            'titulo': 'Receitas vs Despesas',
            'descricao': 'Comparativo entre receitas e despesas com tendência temporal.',
            'categoria': 'GRAFICO',
            'icone': 'bi-bar-chart',
            'tamanho_padrao': 'lg',
            'ordem_padrao': 6,
        },
        {
            'chave': 'lista_contas_pagar',
            'titulo': 'Contas a Pagar',
            'descricao': 'Lista das contas a pagar mais urgentes.',
            'categoria': 'LISTA',
            'icone': 'bi-credit-card',
            'tamanho_padrao': 'md',
            'ordem_padrao': 7,
        },
        {
            'chave': 'lista_contas_receber',
            'titulo': 'Contas a Receber',
            'descricao': 'Lista dos recebimentos aguardados.',
            'categoria': 'LISTA',
            'icone': 'bi-cash-coin',
            'tamanho_padrao': 'md',
            'ordem_padrao': 8,
        },
        {
            'chave': 'acoes_rapidas',
            'titulo': 'Ações Rápidas',
            'descricao': 'Atalhos para lançamentos e conciliações.',
            'categoria': 'ACAO',
            'icone': 'bi-lightning-charge',
            'tamanho_padrao': 'md',
            'ordem_padrao': 9,
        },
    ]

    for data in widgets:
        Widget.objects.update_or_create(
            chave=data['chave'],
            defaults=data,
        )


def delete_default_widgets(apps, schema_editor):
    Widget = apps.get_model('gestao_rural', 'FinanceiroWidgetCatalogo')
    Widget.objects.filter(
        chave__in=[
            'kpi_receita',
            'kpi_despesa',
            'kpi_saldo',
            'kpi_lucro',
            'grafico_fluxo_caixa',
            'grafico_receitas_despesas',
            'lista_contas_pagar',
            'lista_contas_receber',
            'acoes_rapidas',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gestao_rural', '0021_alter_iatf_veterinario'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinanceiroWidgetCatalogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chave', models.CharField(max_length=100, unique=True, verbose_name='Chave')),
                ('titulo', models.CharField(max_length=120, verbose_name='Título')),
                ('descricao', models.TextField(blank=True, verbose_name='Descrição')),
                (
                    'categoria',
                    models.CharField(
                        choices=[('KPI', 'Indicadores'), ('GRAFICO', 'Gráficos'), ('LISTA', 'Listas'), ('ACAO', 'Ações Rápidas')],
                        default='KPI',
                        max_length=20,
                        verbose_name='Categoria',
                    ),
                ),
                ('icone', models.CharField(blank=True, max_length=60, verbose_name='Ícone')),
                (
                    'tamanho_padrao',
                    models.CharField(
                        choices=[('sm', 'Pequeno'), ('md', 'Médio'), ('lg', 'Grande')],
                        default='md',
                        max_length=5,
                        verbose_name='Tamanho Padrão',
                    ),
                ),
                ('ordem_padrao', models.PositiveIntegerField(default=0, verbose_name='Ordem Padrão')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('metadados', models.JSONField(blank=True, default=dict, verbose_name='Metadados')),
            ],
            options={
                'verbose_name': 'Widget Financeiro',
                'verbose_name_plural': 'Widgets Financeiros',
                'ordering': ['categoria', 'ordem_padrao', 'titulo'],
            },
        ),
        migrations.CreateModel(
            name='FinanceiroDashboardPreferencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'layout_config',
                    models.JSONField(
                        default=gestao_rural.models_financeiro.default_layout_config,
                        help_text='Definição das seções, colunas e widgets do usuário.',
                        verbose_name='Layout Config',
                    ),
                ),
                (
                    'filtros_config',
                    models.JSONField(
                        default=gestao_rural.models_financeiro.default_filters_config,
                        help_text='Seleções de filtros globais preferidos.',
                        verbose_name='Filtros Config',
                    ),
                ),
                (
                    'widgets_personalizados',
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text='Ajustes individuais por widget (cores, limites, metas, etc).',
                        verbose_name='Widgets Personalizados',
                    ),
                ),
                (
                    'modo_comparativo',
                    models.JSONField(
                        default=gestao_rural.models_financeiro.default_comparativo_config,
                        verbose_name='Modo Comparativo',
                    ),
                ),
                ('ultima_visualizacao', models.DateTimeField(blank=True, null=True, verbose_name='Última Visualização')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                (
                    'propriedade',
                    models.ForeignKey(
                        blank=True,
                        help_text='Quando vazio, a preferência é global para o usuário.',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='dashboards_financeiro',
                        to='gestao_rural.propriedade',
                    ),
                ),
                (
                    'usuario',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='preferencias_financeiro',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Preferência de Dashboard Financeiro',
                'verbose_name_plural': 'Preferências de Dashboard Financeiro',
            },
        ),
        migrations.AddConstraint(
            model_name='financeirodashboardpreferencia',
            constraint=models.UniqueConstraint(
                fields=('usuario', 'propriedade'),
                name='unique_preferencia_dashboard_financeiro',
            ),
        ),
        migrations.RunPython(create_default_widgets, delete_default_widgets),
    ]

