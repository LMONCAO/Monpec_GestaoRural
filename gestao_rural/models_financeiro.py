"""Modelos centrais do novo módulo Financeiro."""
from decimal import Decimal
from copy import deepcopy

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


DEFAULT_FINANCEIRO_LAYOUT = {
    "cards": [
        {"id": "saldo_atual", "titulo": "Saldo Atual", "tamanho": "md"},
        {"id": "fluxo_mensal", "titulo": "Fluxo Mensal", "tamanho": "lg"},
    ],
    "tabelas": [
        {"id": "lancamentos_recent", "titulo": "Últimos Lançamentos", "limite": 10},
    ],
    "graficos": [
        {"id": "classificacao_despesas", "titulo": "Despesas por Categoria"},
        {"id": "evolucao_saldo", "titulo": "Evolução do Saldo"},
    ],
}

DEFAULT_FILTERS_CONFIG = {
    "periodo": {"tipo": "mes_atual"},
    "contas": [],
    "centros_custo": [],
    "categorias": [],
    "status": "todos",
}

DEFAULT_COMPARATIVO_CONFIG = {
    "ativo": False,
    "referencia": {"tipo": "anterior", "periodos": 1},
    "metricas": ["entradas", "saidas", "saldo"],
}


def default_layout_config():
    """Retorna layout padrão do dashboard financeiro."""
    return deepcopy(DEFAULT_FINANCEIRO_LAYOUT)


def default_filters_config():
    """Retorna as seleções padrão de filtros do dashboard financeiro."""
    return deepcopy(DEFAULT_FILTERS_CONFIG)


def default_comparativo_config():
    """Configuração inicial para o modo comparativo do dashboard."""
    return deepcopy(DEFAULT_COMPARATIVO_CONFIG)


class TimeStampedModel(models.Model):
    """Base reutilizável com campos padrão de auditoria."""

    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        abstract = True


class CategoriaFinanceira(TimeStampedModel):
    """Categoria de classificação dos lançamentos (receitas, despesas, transferências)."""

    TIPO_RECEITA = "RECEITA"
    TIPO_DESPESA = "DESPESA"
    TIPO_TRANSFERENCIA = "TRANSFERENCIA"

    TIPOS = [
        (TIPO_RECEITA, "Receita"),
        (TIPO_DESPESA, "Despesa"),
        (TIPO_TRANSFERENCIA, "Transferência"),
    ]

    propriedade = models.ForeignKey(
        "Propriedade",
        on_delete=models.CASCADE,
        related_name="categorias_financeiras",
        null=True,
        blank=True,
        help_text="Quando vazio, a categoria fica disponível para todas as propriedades.",
    )
    nome = models.CharField("Nome", max_length=120)
    tipo = models.CharField("Tipo", max_length=15, choices=TIPOS)
    descricao = models.TextField("Descrição", blank=True)
    categoria_pai = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="subcategorias",
        null=True,
        blank=True,
    )
    cor = models.CharField(
        "Cor de Destaque",
        max_length=7,
        blank=True,
        help_text="Utilizada em gráficos e dashboards (HEX, ex: #4F46E5).",
    )
    ativa = models.BooleanField("Ativa", default=True)

    class Meta:
        verbose_name = "Categoria Financeira"
        verbose_name_plural = "Categorias Financeiras"
        ordering = ["tipo", "nome"]
        unique_together = (("propriedade", "nome", "tipo"),)

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class CentroCusto(TimeStampedModel):
    """Centros de custo para segmentar análises financeiras."""

    TIPO_OPERACIONAL = "OPERACIONAL"
    TIPO_ADMINISTRATIVO = "ADMINISTRATIVO"
    TIPO_INVESTIMENTO = "INVESTIMENTO"

    TIPOS = [
        (TIPO_OPERACIONAL, "Operacional"),
        (TIPO_ADMINISTRATIVO, "Administrativo"),
        (TIPO_INVESTIMENTO, "Investimento"),
    ]

    propriedade = models.ForeignKey(
        "Propriedade",
        on_delete=models.CASCADE,
        related_name="centros_custo_financeiros",
    )
    nome = models.CharField("Nome", max_length=120)
    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=TIPOS,
        default=TIPO_OPERACIONAL,
    )
    descricao = models.TextField("Descrição", blank=True)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Centro de Custo"
        verbose_name_plural = "Centros de Custo"
        unique_together = (("propriedade", "nome"),)
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class PlanoConta(TimeStampedModel):
    """Plano de contas contábil simplificado para lançamentos e integrações."""

    TIPO_RECEITA = "RECEITA"
    TIPO_DESPESA = "DESPESA"
    TIPO_TRANSFERENCIA = "TRANSFERENCIA"

    TIPOS = [
        (TIPO_RECEITA, "Receita"),
        (TIPO_DESPESA, "Despesa"),
        (TIPO_TRANSFERENCIA, "Transferência"),
    ]

    propriedade = models.ForeignKey(
        "Propriedade",
        on_delete=models.CASCADE,
        related_name="planos_conta",
        null=True,
        blank=True,
        help_text="Quando vazio, o plano fica disponível para todas as propriedades.",
    )
    codigo = models.CharField("Código", max_length=20)
    nome = models.CharField("Nome", max_length=120)
    tipo = models.CharField("Tipo", max_length=15, choices=TIPOS)
    descricao = models.TextField("Descrição", blank=True)
    categoria_financeira = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.SET_NULL,
        related_name="planos_conta",
        null=True,
        blank=True,
    )
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        verbose_name = "Plano de Conta"
        verbose_name_plural = "Planos de Contas"
        unique_together = (("propriedade", "codigo"),)
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"


class ContaFinanceira(TimeStampedModel):
    """Contas financeiras (caixa, bancos, investimentos)."""

    TIPO_CAIXA = "CAIXA"
    TIPO_CORRENTE = "CORRENTE"
    TIPO_POUPANCA = "POUPANCA"
    TIPO_INVESTIMENTO = "INVESTIMENTO"

    TIPOS = [
        (TIPO_CAIXA, "Caixa"),
        (TIPO_CORRENTE, "Conta Corrente"),
        (TIPO_POUPANCA, "Poupança"),
        (TIPO_INVESTIMENTO, "Investimento"),
    ]

    propriedade = models.ForeignKey(
        "Propriedade",
        on_delete=models.CASCADE,
        related_name="contas_financeiras",
    )
    nome = models.CharField("Nome", max_length=120)
    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=TIPOS,
        default=TIPO_CORRENTE,
    )
    banco = models.CharField("Banco", max_length=120, blank=True)
    agencia = models.CharField("Agência", max_length=20, blank=True)
    numero_conta = models.CharField("Número da Conta", max_length=20, blank=True)
    saldo_inicial = models.DecimalField(
        "Saldo de Abertura",
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    data_saldo_inicial = models.DateField(
        "Data do Saldo Inicial",
        default=timezone.now,
    )
    permite_negativo = models.BooleanField(
        "Permitir saldo negativo",
        default=False,
        help_text="Quando desativado, o sistema alerta antes de gerar saldo negativo.",
    )
    ativa = models.BooleanField("Ativa", default=True)

    class Meta:
        verbose_name = "Conta Financeira"
        verbose_name_plural = "Contas Financeiras"
        unique_together = (("propriedade", "nome"),)
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} - {self.propriedade}"


class LancamentoFinanceiroQuerySet(models.QuerySet):
    """Consultas utilitárias para lançamentos financeiros."""

    def receitas(self):
        return self.filter(tipo=CategoriaFinanceira.TIPO_RECEITA)

    def despesas(self):
        return self.filter(tipo=CategoriaFinanceira.TIPO_DESPESA)

    def transferencias(self):
        return self.filter(tipo=CategoriaFinanceira.TIPO_TRANSFERENCIA)

    def pendentes(self):
        return self.filter(status=LancamentoFinanceiro.STATUS_PENDENTE)

    def quitados(self):
        return self.filter(status=LancamentoFinanceiro.STATUS_QUITADO)

    def atrasados(self):
        hoje = timezone.localdate()
        return self.filter(
            status=LancamentoFinanceiro.STATUS_PENDENTE,
            data_vencimento__lt=hoje,
        )


class LancamentoFinanceiro(TimeStampedModel):
    """Lançamento financeiro unificado (receitas, despesas e transferências)."""

    FORMA_DINHEIRO = "DINHEIRO"
    FORMA_PIX = "PIX"
    FORMA_TRANSFERENCIA = "TRANSFERENCIA"
    FORMA_CARTAO = "CARTAO"
    FORMA_BOLETO = "BOLETO"
    FORMA_CHEQUE = "CHEQUE"

    FORMAS_PAGAMENTO = [
        (FORMA_DINHEIRO, "Dinheiro"),
        (FORMA_PIX, "PIX"),
        (FORMA_TRANSFERENCIA, "Transferência"),
        (FORMA_CARTAO, "Cartão"),
        (FORMA_BOLETO, "Boleto"),
        (FORMA_CHEQUE, "Cheque"),
    ]

    STATUS_PENDENTE = "PENDENTE"
    STATUS_QUITADO = "QUITADO"
    STATUS_CANCELADO = "CANCELADO"

    STATUS_CHOICES = [
        (STATUS_PENDENTE, "Pendente"),
        (STATUS_QUITADO, "Quitado"),
        (STATUS_CANCELADO, "Cancelado"),
    ]

    propriedade = models.ForeignKey(
        "Propriedade",
        on_delete=models.CASCADE,
        related_name="lancamentos_financeiros",
    )
    categoria = models.ForeignKey(
        CategoriaFinanceira,
        on_delete=models.PROTECT,
        related_name="lancamentos",
    )
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.SET_NULL,
        related_name="lancamentos",
        null=True,
        blank=True,
    )
    conta_origem = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name="lancamentos_saida",
        null=True,
        blank=True,
        help_text="Obrigatória para despesas e transferências.",
    )
    conta_destino = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name="lancamentos_entrada",
        null=True,
        blank=True,
        help_text="Utilizada em receitas e transferências.",
    )
    tipo = models.CharField(
        "Tipo do lançamento",
        max_length=15,
        choices=CategoriaFinanceira.TIPOS,
        help_text="Preenchido automaticamente a partir da categoria.",
    )
    descricao = models.CharField("Descrição", max_length=255)
    valor = models.DecimalField("Valor", max_digits=14, decimal_places=2)
    data_competencia = models.DateField(
        "Data de competência",
        help_text="Data em que a receita/despesa ocorreu.",
    )
    data_vencimento = models.DateField(
        "Data de vencimento",
        help_text="Usada para controle de pendências.",
    )
    data_quitacao = models.DateField("Data de quitação", null=True, blank=True)
    forma_pagamento = models.CharField(
        "Forma de pagamento",
        max_length=15,
        choices=FORMAS_PAGAMENTO,
        default=FORMA_PIX,
    )
    status = models.CharField(
        "Status",
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE,
    )
    documento_referencia = models.CharField(
        "Documento de referência",
        max_length=120,
        blank=True,
    )
    observacoes = models.TextField("Observações", blank=True)

    objects = LancamentoFinanceiroQuerySet.as_manager()

    class Meta:
        verbose_name = "Lançamento Financeiro"
        verbose_name_plural = "Lançamentos Financeiros"
        ordering = ["-data_competencia", "-id"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} - {self.valor}"

    def marcar_como_quitado(self, data=None):
        """Atualiza o status e a data de quitação."""
        self.status = self.STATUS_QUITADO
        self.data_quitacao = data or timezone.localdate()
        self.save(update_fields=["status", "data_quitacao", "atualizado_em"])

    def cancelar(self, motivo=None):
        """Cancela o lançamento registrando motivo (opcional)."""
        self.status = self.STATUS_CANCELADO
        if motivo:
            prefixo = f"[Cancelado] {motivo}"
            self.observacoes = (
                f"{prefixo}\n{self.observacoes}" if self.observacoes else prefixo
            )
        self.save(update_fields=["status", "observacoes", "atualizado_em"])

    def atualizar_tipo_por_categoria(self):
        """Garante coerência do tipo com a categoria selecionada."""
        if self.categoria:
            if self.tipo != self.categoria.tipo:
                self.tipo = self.categoria.tipo

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.tipo == CategoriaFinanceira.TIPO_TRANSFERENCIA:
            if not self.conta_origem or not self.conta_destino:
                raise ValidationError(
                    "Transferências exigem conta origem e conta destino."
                )
            if self.conta_origem_id == self.conta_destino_id:
                raise ValidationError(
                    "Conta origem e destino devem ser diferentes em transferências."
                )
        elif self.tipo == CategoriaFinanceira.TIPO_RECEITA:
            if not self.conta_destino:
                raise ValidationError("Receitas precisam de uma conta de destino.")
        elif self.tipo == CategoriaFinanceira.TIPO_DESPESA:
            if not self.conta_origem:
                raise ValidationError("Despesas precisam de uma conta de origem.")

        if self.data_quitacao and self.data_quitacao < self.data_competencia:
            raise ValidationError("Data de quitação não pode ser anterior à competência.")

    def save(self, *args, **kwargs):
        self.atualizar_tipo_por_categoria()
        super().save(*args, **kwargs)


class AnexoLancamentoFinanceiro(TimeStampedModel):
    """Anexos vinculados a lançamentos (notas, comprovantes)."""

    lancamento = models.ForeignKey(
        LancamentoFinanceiro,
        on_delete=models.CASCADE,
        related_name="anexos",
    )
    arquivo = models.FileField("Arquivo", upload_to="financeiro/anexos/%Y/%m/")
    nome_original = models.CharField("Nome original", max_length=255, blank=True)

    class Meta:
        verbose_name = "Anexo de Lançamento"
        verbose_name_plural = "Anexos de Lançamentos"

    def __str__(self):
        return self.nome_original or self.arquivo.name


class MovimentoFinanceiro(TimeStampedModel):
    """Movimentação consolidada de saldos em contas financeiras."""

    TIPO_ENTRADA = "ENTRADA"
    TIPO_SAIDA = "SAIDA"
    TIPO_TRANSFERENCIA = "TRANSFERENCIA"
    TIPO_AJUSTE = "AJUSTE"

    ORIGEM_LIQUIDACAO = "LIQUIDACAO"
    ORIGEM_TRANSFERENCIA = "TRANSFERENCIA"
    ORIGEM_SALDO_INICIAL = "SALDO_INICIAL"
    ORIGEM_AJUSTE = "AJUSTE"

    TIPO_CHOICES = [
        (TIPO_ENTRADA, "Entrada"),
        (TIPO_SAIDA, "Saída"),
        (TIPO_TRANSFERENCIA, "Transferência"),
        (TIPO_AJUSTE, "Ajuste Manual"),
    ]
    ORIGEM_CHOICES = [
        (ORIGEM_LIQUIDACAO, "Liquidação de Parcela"),
        (ORIGEM_TRANSFERENCIA, "Transferência entre Contas"),
        (ORIGEM_SALDO_INICIAL, "Saldo Inicial"),
        (ORIGEM_AJUSTE, "Ajuste Manual"),
    ]

    conta = models.ForeignKey(
        ContaFinanceira,
        on_delete=models.PROTECT,
        related_name="movimentos",
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="movimentos_financeiros_criados",
        null=True,
        blank=True,
    )

    tipo = models.CharField("Tipo de Movimento", max_length=15, choices=TIPO_CHOICES)
    origem = models.CharField(
        "Origem do Movimento", max_length=20, choices=ORIGEM_CHOICES
    )
    data_movimento = models.DateField(
        "Data do Movimento", default=timezone.now
    )
    descricao = models.CharField("Descrição", max_length=255)

    valor_bruto = models.DecimalField("Valor", max_digits=14, decimal_places=2)
    valor_taxas = models.DecimalField(
        "Taxas/Descontos",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    valor_liquido = models.DecimalField(
        "Valor Líquido",
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    conciliado = models.BooleanField("Conciliado", default=False)
    conciliado_em = models.DateTimeField("Conciliado em", null=True, blank=True)

    class Meta:
        verbose_name = "Movimento Financeiro"
        verbose_name_plural = "Movimentos Financeiros"
        ordering = ["-data_movimento", "-id"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} ({self.valor_liquido})"

    def clean(self):
        super().clean()
        if self.valor_liquido is None:
            self.valor_liquido = self.valor_bruto - self.valor_taxas

    def save(self, *args, **kwargs):
        if self.valor_liquido is None:
            self.valor_liquido = self.valor_bruto - self.valor_taxas
        super().save(*args, **kwargs)

