from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("gestao_rural", "0033_planejamento_indicadores_enriquecidos"),
    ]

    operations = [
        migrations.DeleteModel(
            name="FinanceiroDashboardPreferencia",
        ),
        migrations.DeleteModel(
            name="FinanceiroWidgetCatalogo",
        ),
        migrations.DeleteModel(
            name="ContaBancaria",
        ),
        migrations.DeleteModel(
            name="LancamentoFinanceiro",
        ),
        migrations.DeleteModel(
            name="CategoriaFinanceira",
        ),
        migrations.CreateModel(
            name="CategoriaFinanceira",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "atualizado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
                ("nome", models.CharField(max_length=120, verbose_name="Nome")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("RECEITA", "Receita"),
                            ("DESPESA", "Despesa"),
                            ("TRANSFERENCIA", "Transferência"),
                        ],
                        max_length=15,
                        verbose_name="Tipo",
                    ),
                ),
                ("descricao", models.TextField(blank=True, verbose_name="Descrição")),
                (
                    "cor",
                    models.CharField(
                        blank=True,
                        help_text="Utilizada em gráficos e dashboards (HEX, ex: #4F46E5).",
                        max_length=7,
                        verbose_name="Cor de Destaque",
                    ),
                ),
                (
                    "ativa",
                    models.BooleanField(default=True, verbose_name="Ativa"),
                ),
            ],
            options={
                "verbose_name": "Categoria Financeira",
                "verbose_name_plural": "Categorias Financeiras",
                "ordering": ["tipo", "nome"],
            },
        ),
        migrations.CreateModel(
            name="CentroCustoFinanceiro",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "atualizado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
                ("nome", models.CharField(max_length=120, verbose_name="Nome")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("OPERACIONAL", "Operacional"),
                            ("ADMINISTRATIVO", "Administrativo"),
                            ("INVESTIMENTO", "Investimento"),
                        ],
                        default="OPERACIONAL",
                        max_length=20,
                        verbose_name="Tipo",
                    ),
                ),
                (
                    "descricao",
                    models.TextField(blank=True, verbose_name="Descrição"),
                ),
                (
                    "ativo",
                    models.BooleanField(default=True, verbose_name="Ativo"),
                ),
                (
                    "propriedade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="centros_custo_financeiros",
                        to="gestao_rural.propriedade",
                    ),
                ),
            ],
            options={
                "verbose_name": "Centro de Custo",
                "verbose_name_plural": "Centros de Custo",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="ContaFinanceira",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "atualizado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
                ("nome", models.CharField(max_length=120, verbose_name="Nome")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("CAIXA", "Caixa"),
                            ("CORRENTE", "Conta Corrente"),
                            ("POUPANCA", "Poupança"),
                            ("INVESTIMENTO", "Investimento"),
                        ],
                        default="CORRENTE",
                        max_length=20,
                        verbose_name="Tipo",
                    ),
                ),
                ("banco", models.CharField(blank=True, max_length=120, verbose_name="Banco")),
                ("agencia", models.CharField(blank=True, max_length=20, verbose_name="Agência")),
                (
                    "numero_conta",
                    models.CharField(blank=True, max_length=20, verbose_name="Número da Conta"),
                ),
                (
                    "saldo_inicial",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=14,
                        verbose_name="Saldo de Abertura",
                    ),
                ),
                (
                    "data_saldo_inicial",
                    models.DateField(
                        default=django.utils.timezone.now,
                        verbose_name="Data do Saldo Inicial",
                    ),
                ),
                (
                    "permite_negativo",
                    models.BooleanField(
                        default=False,
                        help_text="Quando desativado, o sistema alerta antes de gerar saldo negativo.",
                        verbose_name="Permitir saldo negativo",
                    ),
                ),
                (
                    "ativa",
                    models.BooleanField(default=True, verbose_name="Ativa"),
                ),
                (
                    "propriedade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contas_financeiras",
                        to="gestao_rural.propriedade",
                    ),
                ),
            ],
            options={
                "verbose_name": "Conta Financeira",
                "verbose_name_plural": "Contas Financeiras",
                "ordering": ["nome"],
            },
        ),
        migrations.AddField(
            model_name="categoriafinanceira",
            name="categoria_pai",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subcategorias",
                to="gestao_rural.categoriafinanceira",
            ),
        ),
        migrations.AddField(
            model_name="categoriafinanceira",
            name="propriedade",
            field=models.ForeignKey(
                blank=True,
                help_text="Quando vazio, a categoria fica disponível para todas as propriedades.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="categorias_financeiras",
                to="gestao_rural.propriedade",
            ),
        ),
        migrations.CreateModel(
            name="LancamentoFinanceiro",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "atualizado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("RECEITA", "Receita"),
                            ("DESPESA", "Despesa"),
                            ("TRANSFERENCIA", "Transferência"),
                        ],
                        max_length=15,
                        verbose_name="Tipo do lançamento",
                    ),
                ),
                (
                    "descricao",
                    models.CharField(max_length=255, verbose_name="Descrição"),
                ),
                (
                    "valor",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=14,
                        verbose_name="Valor",
                    ),
                ),
                (
                    "data_competencia",
                    models.DateField(
                        help_text="Data em que a receita/despesa ocorreu.",
                        verbose_name="Data de competência",
                    ),
                ),
                (
                    "data_vencimento",
                    models.DateField(
                        help_text="Usada para controle de pendências.",
                        verbose_name="Data de vencimento",
                    ),
                ),
                (
                    "data_quitacao",
                    models.DateField(blank=True, null=True, verbose_name="Data de quitação"),
                ),
                (
                    "forma_pagamento",
                    models.CharField(
                        choices=[
                            ("DINHEIRO", "Dinheiro"),
                            ("PIX", "PIX"),
                            ("TRANSFERENCIA", "Transferência"),
                            ("CARTAO", "Cartão"),
                            ("BOLETO", "Boleto"),
                            ("CHEQUE", "Cheque"),
                        ],
                        default="PIX",
                        max_length=15,
                        verbose_name="Forma de pagamento",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDENTE", "Pendente"),
                            ("QUITADO", "Quitado"),
                            ("CANCELADO", "Cancelado"),
                        ],
                        default="PENDENTE",
                        max_length=15,
                        verbose_name="Status",
                    ),
                ),
                (
                    "documento_referencia",
                    models.CharField(
                        blank=True,
                        max_length=120,
                        verbose_name="Documento de referência",
                    ),
                ),
                ("observacoes", models.TextField(blank=True, verbose_name="Observações")),
                (
                    "categoria",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lancamentos",
                        to="gestao_rural.categoriafinanceira",
                    ),
                ),
                (
                    "centro_custo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lancamentos",
                        to="gestao_rural.centrocustofinanceiro",
                    ),
                ),
                (
                    "conta_destino",
                    models.ForeignKey(
                        blank=True,
                        help_text="Utilizada em receitas e transferências.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lancamentos_entrada",
                        to="gestao_rural.contafinanceira",
                    ),
                ),
                (
                    "conta_origem",
                    models.ForeignKey(
                        blank=True,
                        help_text="Obrigatória para despesas e transferências.",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="lancamentos_saida",
                        to="gestao_rural.contafinanceira",
                    ),
                ),
                (
                    "propriedade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lancamentos_financeiros",
                        to="gestao_rural.propriedade",
                    ),
                ),
            ],
            options={
                "verbose_name": "Lançamento Financeiro",
                "verbose_name_plural": "Lançamentos Financeiros",
                "ordering": ["-data_competencia", "-id"],
            },
        ),
        migrations.CreateModel(
            name="AnexoLancamentoFinanceiro",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "criado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Criado em"),
                ),
                (
                    "atualizado_em",
                    models.DateTimeField(auto_now=True, verbose_name="Atualizado em"),
                ),
                (
                    "arquivo",
                    models.FileField(
                        upload_to="financeiro/anexos/%Y/%m/",
                        verbose_name="Arquivo",
                    ),
                ),
                (
                    "nome_original",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Nome original",
                    ),
                ),
                (
                    "lancamento",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="anexos",
                        to="gestao_rural.lancamentofinanceiro",
                    ),
                ),
            ],
            options={
                "verbose_name": "Anexo de Lançamento",
                "verbose_name_plural": "Anexos de Lançamentos",
            },
        ),
        migrations.AlterUniqueTogether(
            name="categoriafinanceira",
            unique_together={("propriedade", "nome", "tipo")},
        ),
        migrations.AlterUniqueTogether(
            name="centrocustofinanceiro",
            unique_together={("propriedade", "nome")},
        ),
        migrations.AlterUniqueTogether(
            name="contafinanceira",
            unique_together={("propriedade", "nome")},
        ),
    ]





