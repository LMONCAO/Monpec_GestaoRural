# -*- coding: utf-8 -*-
"""
Modelos para Sistema Financeiro Integrado
- Compras
- Notas Fiscais (SEFAZ)
- Integração Financeira
- Fornecedores
"""

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid

from .models import Propriedade
from .models_financeiro import CentroCusto, PlanoConta
from .models_operacional import Equipamento

MESES_CHOICES = (
    (1, "Janeiro"),
    (2, "Fevereiro"),
    (3, "Março"),
    (4, "Abril"),
    (5, "Maio"),
    (6, "Junho"),
    (7, "Julho"),
    (8, "Agosto"),
    (9, "Setembro"),
    (10, "Outubro"),
    (11, "Novembro"),
    (12, "Dezembro"),
)


# ============================================================================
# FORNECEDORES
# ============================================================================

class Fornecedor(models.Model):
    """Cadastro de fornecedores"""
    TIPO_CHOICES = [
        ('RACAO', 'Ração/Insumos'),
        ('MEDICAMENTO', 'Medicamentos'),
        ('EQUIPAMENTO', 'Equipamentos'),
        ('COMBUSTIVEL', 'Combustível'),
        ('SERVICO', 'Serviços'),
        ('OUTROS', 'Outros'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='fornecedores',
        verbose_name="Propriedade",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=200, verbose_name="Nome/Razão Social")
    nome_fantasia = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nome Fantasia"
    )
    cpf_cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CPF/CNPJ"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Fornecedor"
    )
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    
    # Endereço
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    
    # Dados Bancários
    banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco")
    agencia = models.CharField(max_length=10, blank=True, null=True, verbose_name="Agência")
    conta = models.CharField(max_length=20, blank=True, null=True, verbose_name="Conta")
    
    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Avaliação (0-5)",
        help_text="Avaliação do fornecedor"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"


class SetorPropriedade(models.Model):
    """Estrutura organizacional da fazenda para controle de requisições."""

    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name="setores_propriedade",
        verbose_name="Propriedade",
    )
    nome = models.CharField(max_length=120, verbose_name="Nome do Setor")
    codigo = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name="Código Interno",
        help_text="Identificador curto usado em relatórios e integrações.",
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição / Escopo",
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="setores_responsaveis",
        verbose_name="Responsável",
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro",
    )

    class Meta:
        verbose_name = "Setor da Propriedade"
        verbose_name_plural = "Setores da Propriedade"
        unique_together = ("propriedade", "nome")
        ordering = ["propriedade__nome_propriedade", "nome"]

    def __str__(self):
        return f"{self.nome} - {self.propriedade.nome_propriedade}"


class OrcamentoCompraMensal(models.Model):
    """Limite mensal de gastos em compras por propriedade e setor."""

    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name="orcamentos_compras",
        verbose_name="Propriedade",
    )
    setor = models.ForeignKey(
        SetorPropriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orcamentos_mensais",
        verbose_name="Setor",
    )
    ano = models.PositiveIntegerField(verbose_name="Ano")
    mes = models.PositiveSmallIntegerField(choices=MESES_CHOICES, verbose_name="Mês")
    valor_limite = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Limite Mensal (R$)",
    )
    limite_extra = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Limite Extra (R$)",
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orcamentos_compras_criados",
    )
    atualizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orcamentos_compras_atualizados",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Orçamento Mensal de Compras"
        verbose_name_plural = "Orçamentos Mensais de Compras"
        unique_together = ("propriedade", "setor", "ano", "mes")
        ordering = ["-ano", "-mes", "setor__nome"]

    def __str__(self):
        setor_nome = self.setor.nome if self.setor else "Geral"
        return f"{setor_nome} - {self.get_mes_display()}/{self.ano}"

    @property
    def total_limite(self):
        return (self.valor_limite or Decimal("0.00")) + (self.limite_extra or Decimal("0.00"))

    def valor_utilizado(self, ignorar_ordem=None):
        filtros = {
            "propriedade": self.propriedade,
            "data_emissao__year": self.ano,
            "data_emissao__month": self.mes,
        }
        if self.setor_id:
            filtros["setor_id"] = self.setor_id

        qs = OrdemCompra.objects.filter(**filtros).exclude(status="CANCELADA")
        if ignorar_ordem:
            pk = ignorar_ordem.pk if hasattr(ignorar_ordem, "pk") else ignorar_ordem
            qs = qs.exclude(pk=pk)

        total = qs.aggregate(total=Sum("valor_total"))['total']
        return total or Decimal("0.00")

    def saldo_disponivel(self, ignorar_ordem=None):
        saldo = self.total_limite - self.valor_utilizado(ignorar_ordem=ignorar_ordem)
        return saldo if saldo > Decimal("0.00") else Decimal("0.00")

    def percentual_utilizado(self, ignorar_ordem=None):
        total_limite = self.total_limite
        if total_limite == 0:
            return 0
        utilizado = self.valor_utilizado(ignorar_ordem=ignorar_ordem)
        return float((utilizado / total_limite) * 100)

    def excede_limite(self, valor, ignorar_ordem=None):
        if valor <= Decimal("0.00"):
            return False
        saldo = self.total_limite - self.valor_utilizado(ignorar_ordem=ignorar_ordem)
        return valor > saldo


class AjusteOrcamentoCompra(models.Model):
    """Registro de limites extras aprovados para o orçamento mensal."""

    orcamento = models.ForeignKey(
        OrcamentoCompraMensal,
        on_delete=models.CASCADE,
        related_name="ajustes",
        verbose_name="Orçamento",
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor do Ajuste (R$)",
        help_text="Informe o valor adicional aprovado para este mês.",
    )
    justificativa = models.TextField(verbose_name="Justificativa do ajuste")
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ajustes_orcamento_criados",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Ajuste Emergencial de Orçamento"
        verbose_name_plural = "Ajustes Emergenciais de Orçamento"
        ordering = ["-criado_em"]

    def __str__(self):
        sinal = "+" if self.valor >= 0 else ""
        return f"{sinal}{self.valor} em {self.criado_em:%d/%m/%Y}"


class ConviteCotacaoFornecedor(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ENVIADO', 'Enviado'),
        ('RESPONDIDO', 'Respondido'),
        ('CANCELADO', 'Cancelado'),
        ('EXPIRADO', 'Expirado'),
    ]

    requisicao = models.ForeignKey(
        'RequisicaoCompra',
        on_delete=models.CASCADE,
        related_name='convites',
        verbose_name='Requisição'
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='convites_cotacao',
        verbose_name='Fornecedor'
    )
    email_destinatario = models.EmailField(
        blank=True,
        null=True,
        verbose_name='E-mail do destinatário'
    )
    token = models.CharField(
        max_length=32,
        unique=True,
        editable=False
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    enviado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='convites_cotacao_enviados',
        verbose_name='Criado por'
    )
    enviado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de envio'
    )
    data_expiracao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expira em'
    )
    respondido_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Respondido em'
    )
    observacao_resposta = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações do fornecedor'
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Convite de Cotação'
        verbose_name_plural = 'Convites de Cotação'
        ordering = ['-criado_em']
        constraints = [
            models.UniqueConstraint(
                fields=['requisicao', 'fornecedor'],
                name='unique_convite_requisicao_fornecedor'
            )
        ]

    def __str__(self):
        return f"Convite {self.requisicao_id} - {self.fornecedor.nome}"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    @property
    def expirado(self):
        return self.data_expiracao and timezone.now() > self.data_expiracao

    def pode_responder(self):
        return self.status in ['PENDENTE', 'ENVIADO'] and not self.expirado

    def marcar_enviado(self, usuario):
        self.enviado_por = usuario
        self.enviado_em = timezone.now()
        self.status = 'ENVIADO'
        self.save(update_fields=['enviado_por', 'enviado_em', 'status', 'atualizado_em'])

    def marcar_respondido(self, observacao=''):
        self.respondido_em = timezone.now()
        self.status = 'RESPONDIDO'
        self.observacao_resposta = observacao
        self.save(update_fields=['respondido_em', 'status', 'observacao_resposta', 'atualizado_em'])

    def cancelar(self):
        self.status = 'CANCELADO'
        self.save(update_fields=['status', 'atualizado_em'])


# ============================================================================
# PRODUTOS (CADASTRO FISCAL)
# ============================================================================

class CategoriaProduto(models.Model):
    """Categorias de produtos para organização"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Produto(models.Model):
    """Cadastro de produtos sincronizado com a Receita Federal"""
    UNIDADE_MEDIDA_CHOICES = [
        ('UN', 'Unidade'),
        ('KG', 'Quilograma'),
        ('TON', 'Tonelada'),
        ('L', 'Litro'),
        ('M', 'Metro'),
        ('M2', 'Metro Quadrado'),
        ('M3', 'Metro Cúbico'),
        ('SC', 'Saca'),
        ('CX', 'Caixa'),
        ('PC', 'Peça'),
        ('FD', 'Fardo'),
        ('RL', 'Rolo'),
    ]
    
    # Dados Básicos
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código do Produto",
        help_text="Código interno do produto"
    )
    descricao = models.CharField(
        max_length=200,
        verbose_name="Descrição do Produto"
    )
    descricao_completa = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição Completa",
        help_text="Descrição detalhada do produto"
    )
    categoria = models.ForeignKey(
        CategoriaProduto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos',
        verbose_name="Categoria"
    )
    
    # Unidade de Medida
    unidade_medida = models.CharField(
        max_length=10,
        choices=UNIDADE_MEDIDA_CHOICES,
        default='UN',
        verbose_name="Unidade de Medida"
    )
    
    # Dados Fiscais - NCM
    ncm = models.CharField(
        max_length=10,
        verbose_name="NCM",
        help_text="Nomenclatura Comum do Mercosul (ex: 0102.29.00)"
    )
    ncm_descricao = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Descrição do NCM",
        help_text="Descrição oficial do NCM pela Receita"
    )
    ncm_validado = models.BooleanField(
        default=False,
        verbose_name="NCM Validado",
        help_text="Indica se o NCM foi validado com a Receita Federal"
    )
    ncm_data_validacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Validação do NCM"
    )
    
    # Dados Fiscais - CFOP
    cfop_entrada = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="CFOP Entrada",
        help_text="CFOP padrão para compras (ex: 1102)"
    )
    cfop_saida_estadual = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="CFOP Saída Estadual",
        help_text="CFOP padrão para vendas dentro do estado (ex: 5102)"
    )
    cfop_saida_interestadual = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="CFOP Saída Interestadual",
        help_text="CFOP padrão para vendas fora do estado (ex: 6102)"
    )
    
    # Dados Fiscais - Impostos
    cst_icms = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        verbose_name="CST ICMS",
        help_text="Código de Situação Tributária do ICMS"
    )
    aliquota_icms = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Alíquota ICMS (%)"
    )
    cst_ipi = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        verbose_name="CST IPI",
        help_text="Código de Situação Tributária do IPI"
    )
    aliquota_ipi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Alíquota IPI (%)"
    )
    cst_pis = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        verbose_name="CST PIS",
        help_text="Código de Situação Tributária do PIS"
    )
    aliquota_pis = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Alíquota PIS (%)"
    )
    cst_cofins = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        verbose_name="CST COFINS",
        help_text="Código de Situação Tributária do COFINS"
    )
    aliquota_cofins = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Alíquota COFINS (%)"
    )
    
    # Dados Comerciais
    preco_venda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Preço de Venda (R$)"
    )
    preco_custo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Preço de Custo (R$)"
    )
    
    # Status e Controle
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    sincronizado_receita = models.BooleanField(
        default=False,
        verbose_name="Sincronizado com Receita",
        help_text="Indica se os dados foram sincronizados com a Receita Federal"
    )
    data_sincronizacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Última Sincronização"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    # Auditoria
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    usuario_cadastro = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos_cadastrados',
        verbose_name="Usuário que Cadastrou"
    )
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['categoria', 'descricao']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['ncm']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.descricao}"
    
    def clean(self):
        """Validação do modelo"""
        from django.core.exceptions import ValidationError
        
        # Validar formato do NCM (8 dígitos)
        if self.ncm:
            ncm_limpo = self.ncm.replace('.', '').replace('-', '')
            if len(ncm_limpo) != 8 or not ncm_limpo.isdigit():
                raise ValidationError({
                    'ncm': 'NCM deve ter 8 dígitos numéricos (ex: 0102.29.00)'
                })
    
    def save(self, *args, **kwargs):
        """Override save para limpar e formatar NCM"""
        if self.ncm:
            # Remover pontos e traços, depois formatar
            ncm_limpo = self.ncm.replace('.', '').replace('-', '')
            if len(ncm_limpo) == 8:
                self.ncm = f"{ncm_limpo[:4]}.{ncm_limpo[4:6]}.{ncm_limpo[6:]}"
        super().save(*args, **kwargs)


# ============================================================================
# NOTAS FISCAIS (SEFAZ)
# ============================================================================

class NotaFiscal(models.Model):
    """Notas Fiscais Eletrônicas (NF-e)"""
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada (Compra)'),
        ('SAIDA', 'Saída (Venda)'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('AUTORIZADA', 'Autorizada'),
        ('CANCELADA', 'Cancelada'),
        ('REJEITADA', 'Rejeitada'),
        ('INUTILIZADA', 'Inutilizada'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='notas_fiscais',
        verbose_name="Propriedade"
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='notas_fiscais',
        verbose_name="Fornecedor",
        null=True,
        blank=True,
        help_text="Obrigatório para NF-e de entrada (compra)"
    )
    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        related_name='notas_fiscais',
        verbose_name="Cliente",
        null=True,
        blank=True,
        help_text="Obrigatório para NF-e de saída (venda)"
    )
    
    # Dados da NF-e
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='ENTRADA',
        verbose_name="Tipo"
    )
    numero = models.CharField(max_length=50, verbose_name="Número da NF-e")
    serie = models.CharField(max_length=10, default='1', verbose_name="Série")
    chave_acesso = models.CharField(
        max_length=44,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Chave de Acesso",
        help_text="Chave de acesso da NF-e (44 dígitos)"
    )
    
    # Datas
    data_emissao = models.DateField(verbose_name="Data de Emissão")
    data_entrada = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Entrada/Saída"
    )
    
    # Valores
    valor_produtos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor dos Produtos (R$)"
    )
    valor_frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor do Frete (R$)"
    )
    valor_seguro = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor do Seguro (R$)"
    )
    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor do Desconto (R$)"
    )
    valor_outros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Outras Despesas (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )
    
    # Status SEFAZ
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name="Status"
    )
    protocolo_autorizacao = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Protocolo de Autorização"
    )
    data_autorizacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Autorização"
    )
    
    # Arquivos
    arquivo_xml = models.FileField(
        upload_to='nfe/xml/',
        blank=True,
        null=True,
        verbose_name="Arquivo XML"
    )
    arquivo_pdf = models.FileField(
        upload_to='nfe/pdf/',
        blank=True,
        null=True,
        verbose_name="Arquivo PDF (DANFE)"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    importado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Importado por"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Nota Fiscal"
        verbose_name_plural = "Notas Fiscais"
        ordering = ['-data_emissao', 'numero']
        # unique_together removido pois fornecedor/cliente podem ser diferentes
    
    def __str__(self):
        if self.tipo == 'SAIDA' and self.cliente:
            return f"NF-e {self.numero}/{self.serie} - {self.cliente.nome} - {self.data_emissao}"
        elif self.fornecedor:
            return f"NF-e {self.numero}/{self.serie} - {self.fornecedor.nome} - {self.data_emissao}"
        return f"NF-e {self.numero}/{self.serie} - {self.data_emissao}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        self.valor_total = (
            self.valor_produtos +
            self.valor_frete +
            self.valor_seguro +
            self.valor_outros -
            self.valor_desconto
        )
        super().save(*args, **kwargs)


class ItemNotaFiscal(models.Model):
    """Itens da Nota Fiscal"""
    nota_fiscal = models.ForeignKey(
        NotaFiscal,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Nota Fiscal"
    )
    
    # Produto - Referência ao cadastro
    produto = models.ForeignKey(
        Produto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_nota_fiscal',
        verbose_name="Produto",
        help_text="Produto cadastrado (preenche automaticamente os dados fiscais)"
    )
    
    # Produto - Dados manuais (usados quando não há produto cadastrado)
    codigo_produto = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Código do Produto"
    )
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    ncm = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="NCM"
    )
    cfop = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="CFOP"
    )
    
    # Quantidades
    unidade_medida = models.CharField(
        max_length=10,
        default='UN',
        verbose_name="Unidade de Medida"
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Quantidade"
    )
    
    # Valores
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Unitário (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )
    
    # Impostos
    valor_icms = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor ICMS (R$)"
    )
    valor_ipi = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor IPI (R$)"
    )
    
    class Meta:
        verbose_name = "Item da Nota Fiscal"
        verbose_name_plural = "Itens da Nota Fiscal"
        ordering = ['nota_fiscal', 'descricao']
    
    def __str__(self):
        return f"{self.nota_fiscal.numero} - {self.descricao}"
    
    def save(self, *args, **kwargs):
        # Se há produto cadastrado, preencher dados automaticamente
        if self.produto:
            if not self.codigo_produto:
                self.codigo_produto = self.produto.codigo
            if not self.descricao:
                self.descricao = self.produto.descricao
            if not self.ncm:
                self.ncm = self.produto.ncm
            if not self.unidade_medida:
                self.unidade_medida = self.produto.unidade_medida
            
            # Determinar CFOP baseado no tipo de nota e UF
            if self.nota_fiscal.tipo == 'ENTRADA' and self.produto.cfop_entrada:
                self.cfop = self.produto.cfop_entrada
            elif self.nota_fiscal.tipo == 'SAIDA':
                # Verificar se é interestadual (simplificado - pode melhorar)
                if self.nota_fiscal.cliente:
                    cliente_uf = getattr(self.nota_fiscal.cliente, 'estado', '')
                    propriedade_uf = getattr(self.nota_fiscal.propriedade, 'estado', '')
                    if cliente_uf and propriedade_uf and cliente_uf != propriedade_uf:
                        # Interestadual
                        if self.produto.cfop_saida_interestadual:
                            self.cfop = self.produto.cfop_saida_interestadual
                    else:
                        # Estadual
                        if self.produto.cfop_saida_estadual:
                            self.cfop = self.produto.cfop_saida_estadual
        
        # Calcular valor total
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)


# ============================================================================
# REQUISIÇÕES E WORKFLOW DE COMPRAS
# ============================================================================


class RequisicaoCompra(models.Model):
    """Fluxo de requisição aberto na fazenda"""
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('ENVIADA', 'Aguardando Aprovação do Gerente'),
        ('REPROVADA_GERENCIA', 'Reprovada pela Gerência'),
        ('APROVADA_GERENCIA', 'Aprovada pela Gerência'),
        ('EM_COTACAO', 'Em Cotação'),
        ('AGUARDANDO_APROVACAO_COMPRAS', 'Aguardando Aprovação de Compras'),
        ('REPROVADA_COMPRAS', 'Reprovada por Compras'),
        ('APROVADA_COMPRAS', 'Aprovada por Compras'),
        ('ORDEM_EMITIDA', 'Ordem de Compra Emitida'),
        ('AGUARDANDO_RECEBIMENTO', 'Aguardando Recebimento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]

    PRIORIDADE_CHOICES = [
        ('BAIXA', 'Baixa'),
        ('MEDIA', 'Média'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    ]

    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='requisicoes_compra',
        verbose_name="Propriedade"
    )
    solicitante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requisicoes_compra_criadas',
        verbose_name="Solicitante"
    )
    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name="Status"
    )
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='MEDIA',
        verbose_name="Prioridade"
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    justificativa = models.TextField(verbose_name="Justificativa")
    data_necessidade = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Necessidade"
    )
    setor = models.ForeignKey(
        SetorPropriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisicoes",
        verbose_name="Setor Solicitante"
    )
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisicoes_compra",
        verbose_name="Máquina/Equipamento"
    )
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisicoes_compra",
        verbose_name="Centro de Custo"
    )
    centro_custo_descricao = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Centro de Custo (Manual)"
    )
    plano_conta = models.ForeignKey(
        PlanoConta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requisicoes_compra",
        verbose_name="Plano de Contas"
    )
    observacoes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações"
    )
    numero = models.CharField(
        max_length=25,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Número da Requisição"
    )
    motivo_cancelamento = models.TextField(
        null=True,
        blank=True,
        verbose_name="Motivo do Cancelamento"
    )
    ordem_compra = models.ForeignKey(
        'OrdemCompra',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requisicoes_origem',
        verbose_name="Ordem de Compra Gerada"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )
    enviado_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Envio"
    )
    concluido_em = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Conclusão"
    )

    class Meta:
        verbose_name = "Requisição de Compra"
        verbose_name_plural = "Requisições de Compra"
        ordering = ['-criado_em']

    def __str__(self):
        numero = f"{self.numero} - " if self.numero else ""
        return f"{numero}{self.titulo} - {self.get_status_display()}"

    @property
    def total_estimado(self):
        return sum(item.valor_estimado_total for item in self.itens.all())

    @classmethod
    def gerar_proximo_numero(cls, propriedade):
        from django.utils import timezone

        ano = timezone.now().year
        base = f"REQ-{ano}"
        ultimo = (
            cls.objects.filter(propriedade=propriedade, numero__startswith=base)
            .order_by('-numero')
            .first()
        )
        sequencial = 1
        if ultimo and ultimo.numero:
            try:
                sequencial = int(ultimo.numero.split('/')[-1]) + 1
            except (ValueError, IndexError):
                sequencial = cls.objects.filter(
                    propriedade=propriedade,
                    numero__startswith=base
                ).count() + 1
        return f"{base}/{sequencial:04d}"

    def save(self, *args, **kwargs):
        from django.utils import timezone

        if not self.numero and self.propriedade_id:
            self.numero = self.gerar_proximo_numero(self.propriedade)
        if not self.criado_em:
            self.criado_em = timezone.now()
        super().save(*args, **kwargs)

    @property
    def centro_custo_display(self):
        if self.centro_custo:
            return str(self.centro_custo)
        return self.centro_custo_descricao or ""

    @property
    def plano_conta_display(self):
        return str(self.plano_conta) if self.plano_conta else ""

    @property
    def setor_display(self):
        return str(self.setor) if self.setor else ""


class ItemRequisicaoCompra(models.Model):
    """Itens que compõem a requisição"""
    UNIDADE_CHOICES = [
        ('UN', 'Unidade'),
        ('KG', 'Quilograma'),
        ('L', 'Litro'),
        ('SC', 'Saca'),
        ('CX', 'Caixa'),
        ('MT', 'Metro'),
        ('OUTROS', 'Outros'),
    ]

    requisicao = models.ForeignKey(
        RequisicaoCompra,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Requisição"
    )
    descricao = models.CharField(
        max_length=255,
        verbose_name="Descrição do Item"
    )
    unidade_medida = models.CharField(
        max_length=10,
        choices=UNIDADE_CHOICES,
        default='UN',
        verbose_name="Unidade de Medida"
    )
    quantidade = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Quantidade"
    )
    valor_estimado_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Estimado Unitário (R$)"
    )
    fornecedor_preferencial = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Fornecedor Preferencial"
    )
    observacoes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações do Item"
    )

    class Meta:
        verbose_name = "Item de Requisição de Compra"
        verbose_name_plural = "Itens de Requisição de Compra"
        ordering = ['requisicao', 'descricao']

    def __str__(self):
        return f"{self.descricao} ({self.quantidade} {self.unidade_medida})"

    @property
    def valor_estimado_total(self):
        return self.quantidade * self.valor_estimado_unitario


class AprovacaoRequisicaoCompra(models.Model):
    """Histórico de aprovações por etapa"""
    ETAPA_CHOICES = [
        ('GERENCIA', 'Gerência da Fazenda'),
        ('COMPRADOR', 'Comprador'),
        ('RESPONSAVEL_COMPRAS', 'Responsável de Compras'),
        ('RECEBIMENTO', 'Recebimento'),
        ('FINANCEIRO', 'Financeiro'),
    ]

    DECISAO_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('REPROVADO', 'Reprovado'),
        ('DEVOLVIDO', 'Devolvido para Ajustes'),
    ]

    requisicao = models.ForeignKey(
        RequisicaoCompra,
        on_delete=models.CASCADE,
        related_name='aprovacoes',
        verbose_name="Requisição"
    )
    etapa = models.CharField(
        max_length=30,
        choices=ETAPA_CHOICES,
        verbose_name="Etapa"
    )
    decisao = models.CharField(
        max_length=20,
        choices=DECISAO_CHOICES,
        default='PENDENTE',
        verbose_name="Decisão"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aprovacoes_requisicao',
        verbose_name="Usuário"
    )
    comentario = models.TextField(
        null=True,
        blank=True,
        verbose_name="Comentário"
    )
    data_decisao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data da Decisão"
    )

    class Meta:
        verbose_name = "Aprovação de Requisição"
        verbose_name_plural = "Aprovações de Requisição"
        ordering = ['-data_decisao']

    def __str__(self):
        return f"{self.requisicao_id} - {self.get_etapa_display()} - {self.get_decisao_display()}"


class CotacaoFornecedor(models.Model):
    """Cotações coletadas pelo comprador"""
    STATUS_CHOICES = [
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('RECEBIDA', 'Recebida'),
        ('SELECIONADA', 'Selecionada'),
        ('NAO_SELECIONADA', 'Não Selecionada'),
        ('CANCELADA', 'Cancelada'),
    ]

    requisicao = models.ForeignKey(
        RequisicaoCompra,
        on_delete=models.CASCADE,
        related_name='cotacoes',
        verbose_name="Requisição"
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='cotacoes',
        verbose_name="Fornecedor"
    )
    comprador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cotacoes_registradas',
        verbose_name="Comprador Responsável"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EM_ANDAMENTO',
        verbose_name="Status"
    )
    prazo_entrega_estimado = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Prazo de Entrega Estimado"
    )
    validade_proposta = models.DateField(
        null=True,
        blank=True,
        verbose_name="Validade da Proposta"
    )
    condicoes_pagamento = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Condições de Pagamento"
    )
    valor_frete = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor do Frete (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Total Cotado (R$)"
    )
    observacoes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações"
    )
    anexo_proposta = models.FileField(
        upload_to='compras/cotacoes/',
        null=True,
        blank=True,
        verbose_name="Proposta Anexada"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Registro"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Cotação de Fornecedor"
        verbose_name_plural = "Cotações de Fornecedores"
        ordering = ['-criado_em']

    def __str__(self):
        return f"Cotação {self.fornecedor.nome} - {self.get_status_display()}"


class ItemCotacaoFornecedor(models.Model):
    """Itens de uma cotação por fornecedor"""
    cotacao = models.ForeignKey(
        CotacaoFornecedor,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Cotação"
    )
    item_requisicao = models.ForeignKey(
        ItemRequisicaoCompra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_cotados',
        verbose_name="Item da Requisição"
    )
    descricao = models.CharField(
        max_length=255,
        verbose_name="Descrição"
    )
    unidade_medida = models.CharField(
        max_length=10,
        default='UN',
        verbose_name="Unidade"
    )
    quantidade = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name="Quantidade"
    )
    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Unitário (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )

    class Meta:
        verbose_name = "Item de Cotação"
        verbose_name_plural = "Itens de Cotação"
        ordering = ['cotacao', 'descricao']

    def __str__(self):
        return f"{self.cotacao_id} - {self.descricao}"

    def save(self, *args, **kwargs):
        self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)


class RecebimentoCompra(models.Model):
    """Registro do recebimento físico dos materiais"""
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('RECEBIDO', 'Recebido'),
        ('DIVERGENCIA', 'Divergência'),
        ('CANCELADO', 'Cancelado'),
    ]

    ordem_compra = models.ForeignKey(
        'OrdemCompra',
        on_delete=models.CASCADE,
        related_name='recebimentos',
        verbose_name="Ordem de Compra"
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recebimentos_registrados',
        verbose_name="Responsável Pelo Recebimento"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name="Status"
    )
    data_prevista = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data Prevista"
    )
    data_recebimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Recebimento"
    )
    observacoes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações"
    )
    comprovante_assinado = models.FileField(
        upload_to='compras/recebimentos/',
        null=True,
        blank=True,
        verbose_name="Comprovante Assinado"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Registro"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Atualização"
    )

    class Meta:
        verbose_name = "Recebimento de Compra"
        verbose_name_plural = "Recebimentos de Compra"
        ordering = ['-criado_em']

    def __str__(self):
        return f"Recebimento OC {self.ordem_compra.numero_ordem} - {self.get_status_display()}"


class ItemRecebimentoCompra(models.Model):
    """Itens conferidos no recebimento"""
    recebimento = models.ForeignKey(
        RecebimentoCompra,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Recebimento"
    )
    item_ordem = models.ForeignKey(
        'ItemOrdemCompra',
        on_delete=models.CASCADE,
        related_name='recebimentos',
        verbose_name="Item da Ordem"
    )
    quantidade_recebida = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.000'))],
        verbose_name="Quantidade Recebida"
    )
    divergencia = models.BooleanField(
        default=False,
        verbose_name="Possui Divergência?"
    )
    justificativa_divergencia = models.TextField(
        null=True,
        blank=True,
        verbose_name="Justificativa da Divergência"
    )

    class Meta:
        verbose_name = "Item Recebido"
        verbose_name_plural = "Itens Recebidos"
        ordering = ['recebimento', 'item_ordem']

    def __str__(self):
        return f"{self.recebimento_id} - {self.item_ordem_id}"


class EventoFluxoCompra(models.Model):
    """Trilha de auditoria do processo"""
    ETAPA_CHOICES = [
        ('CRIACAO', 'Criação'),
        ('ENVIO', 'Envio para Aprovação'),
        ('APROVACAO_GERENCIA', 'Aprovação Gerência'),
        ('COTACAO', 'Cotação'),
        ('APROVACAO_COMPRAS', 'Aprovação Compras'),
        ('EMISSAO_OC', 'Emissão de OC'),
        ('RECEBIMENTO', 'Recebimento'),
        ('FINANCEIRO', 'Financeiro'),
        ('AUTORIZACAO_SETOR', 'Autorização do Setor'),
        ('CANCELAMENTO', 'Cancelamento'),
        ('OUTROS', 'Outros'),
    ]

    requisicao = models.ForeignKey(
        RequisicaoCompra,
        on_delete=models.CASCADE,
        related_name='eventos_fluxo',
        verbose_name="Requisição"
    )
    etapa = models.CharField(
        max_length=40,
        choices=ETAPA_CHOICES,
        default='OUTROS',
        verbose_name="Etapa"
    )
    status_anterior = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Status Anterior"
    )
    status_novo = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name="Status Novo"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_fluxo_compra',
        verbose_name="Usuário"
    )
    comentario = models.TextField(
        null=True,
        blank=True,
        verbose_name="Comentário"
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data do Evento"
    )

    class Meta:
        verbose_name = "Evento do Fluxo de Compras"
        verbose_name_plural = "Eventos do Fluxo de Compras"
        ordering = ['-criado_em']

    def __str__(self):
        return f"Evento {self.get_etapa_display()} - {self.criado_em:%d/%m/%Y %H:%M}"


# ============================================================================
# COMPRAS
# ============================================================================

class OrdemCompra(models.Model):
    """Ordem de Compra"""

    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('APROVADA', 'Aprovada'),
        ('ENVIADA', 'Enviada ao Fornecedor'),
        ('PARCIAL', 'Recebimento Parcial'),
        ('RECEBIDA', 'Recebida Completa'),
        ('CANCELADA', 'Cancelada'),
    ]

    AUTORIZACAO_SETOR_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('AUTORIZADA', 'Autorizada'),
        ('NEGADA', 'Negada'),
    ]

    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='ordens_compra',
        verbose_name="Propriedade"
    )
    requisicao_origem = models.ForeignKey(
        RequisicaoCompra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_geradas',
        verbose_name="Requisição de Origem"
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='ordens_compra',
        verbose_name="Fornecedor"
    )
    setor = models.ForeignKey(
        SetorPropriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_compra',
        verbose_name="Setor Responsável"
    )
    plano_conta = models.ForeignKey(
        PlanoConta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_compra',
        verbose_name="Plano de Contas"
    )
    centro_custo = models.ForeignKey(
        CentroCusto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_compra',
        verbose_name="Centro de Custo"
    )
    centro_custo_descricao = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name="Centro de Custo (Manual)"
    )

    # Dados da Ordem
    numero_ordem = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número da Ordem"
    )
    data_emissao = models.DateField(verbose_name="Data de Emissão")
    data_entrega_prevista = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Entrega Prevista"
    )
    data_recebimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Recebimento"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name="Status"
    )
    autorizacao_setor_status = models.CharField(
        max_length=15,
        choices=AUTORIZACAO_SETOR_CHOICES,
        default='PENDENTE',
        verbose_name="Status Autorização Setor"
    )
    autorizacao_setor_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_compra_autorizadas_setor',
        verbose_name="Responsável Autorização Setor"
    )
    autorizacao_setor_data = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data Autorização Setor"
    )
    autorizacao_setor_observacoes = models.TextField(
        null=True,
        blank=True,
        verbose_name="Observações da Autorização do Setor"
    )

    # Valores
    valor_produtos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Valor dos Produtos (R$)"
    )
    valor_frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor do Frete (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Valor Total (R$)"
    )

    # Condições
    condicoes_pagamento = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Condições de Pagamento"
    )
    forma_pagamento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Forma de Pagamento"
    )

    # Relacionamento com NF-e
    nota_fiscal = models.ForeignKey(
        NotaFiscal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_compra',
        verbose_name="Nota Fiscal"
    )

    # Aprovação
    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_compra_aprovadas',
        verbose_name="Aprovado por"
    )
    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Aprovação"
    )

    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordens_compra_criadas',
        verbose_name="Criado por"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")

    class Meta:
        verbose_name = "Ordem de Compra"
        verbose_name_plural = "Ordens de Compra"
        ordering = ['-data_emissao', 'numero_ordem']

    def __str__(self):
        return f"OC {self.numero_ordem} - {self.fornecedor.nome}"

    def save(self, *args, **kwargs):
        # Calcular valor total
        self.valor_total = self.valor_produtos + self.valor_frete
        super().save(*args, **kwargs)

    @property
    def setor_autorizado(self):
        return self.autorizacao_setor_status == 'AUTORIZADA'

    @property
    def centro_custo_display(self):
        if self.centro_custo:
            return str(self.centro_custo)
        return self.centro_custo_descricao or ""



    class Meta:
        verbose_name = "Ordem de Compra"
        verbose_name_plural = "Ordens de Compra"
        ordering = ['-data_emissao', 'numero_ordem']

    def __str__(self):
        return f"OC {self.numero_ordem} - {self.fornecedor.nome}"

    def save(self, *args, **kwargs):
        # Calcular valor total
        self.valor_total = self.valor_produtos + self.valor_frete
        super().save(*args, **kwargs)

    @property
    def setor_autorizado(self):
        return self.autorizacao_setor_status == 'AUTORIZADA'

    @property
    def centro_custo_display(self):
        if self.centro_custo:
            return str(self.centro_custo)
        return self.centro_custo_descricao or ""


class ItemOrdemCompra(models.Model):
    """Itens da Ordem de Compra"""
    ordem_compra = models.ForeignKey(
        OrdemCompra,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Ordem de Compra"
    )
    
    # Produto
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    codigo_produto = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Código do Produto"
    )
    unidade_medida = models.CharField(
        max_length=10,
        default='UN',
        verbose_name="Unidade de Medida"
    )
    
    # Quantidades
    quantidade_solicitada = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Quantidade Solicitada"
    )
    quantidade_recebida = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0,
        verbose_name="Quantidade Recebida"
    )
    
    # Valores
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Unitário (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )
    
    # Validade (para produtos perecíveis)
    data_validade = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Validade"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Item da Ordem de Compra"
        verbose_name_plural = "Itens da Ordem de Compra"
        ordering = ['ordem_compra', 'descricao']
    
    def __str__(self):
        return f"{self.ordem_compra.numero_ordem} - {self.descricao}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        if self.quantidade_solicitada and self.valor_unitario:
            self.valor_total = self.quantidade_solicitada * self.valor_unitario
        super().save(*args, **kwargs)


# ============================================================================
# CONTAS A PAGAR E RECEBER
# ============================================================================

class ContaPagar(models.Model):
    """Contas a Pagar"""
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('VENCIDA', 'Vencida'),
        ('PAGA', 'Paga'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='contas_pagar',
        verbose_name="Propriedade"
    )
    
    # Relacionamentos
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contas_pagar',
        verbose_name="Fornecedor"
    )
    ordem_compra = models.ForeignKey(
        OrdemCompra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contas_pagar',
        verbose_name="Ordem de Compra"
    )
    nota_fiscal = models.ForeignKey(
        NotaFiscal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contas_pagar',
        verbose_name="Nota Fiscal"
    )
    
    # Dados da Conta
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    categoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Categoria",
        help_text="Ex: Combustível, Ração, Salário, etc."
    )
    
    # Valores e Datas
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor (R$)"
    )
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Pagamento"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name="Status"
    )
    
    # Forma de Pagamento
    forma_pagamento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Forma de Pagamento"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Conta a Pagar"
        verbose_name_plural = "Contas a Pagar"
        ordering = ['data_vencimento', 'status']
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} - {self.data_vencimento}"
    
    def save(self, *args, **kwargs):
        # Atualizar status baseado na data
        from datetime import date
        if not self.data_pagamento:
            if self.data_vencimento < date.today():
                self.status = 'VENCIDA'
            else:
                self.status = 'PENDENTE'
        else:
            self.status = 'PAGA'
        super().save(*args, **kwargs)


class ContaReceber(models.Model):
    """Contas a Receber"""
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('VENCIDA', 'Vencida'),
        ('RECEBIDA', 'Recebida'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='contas_receber',
        verbose_name="Propriedade"
    )
    
    # Dados da Conta
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    categoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Categoria",
        help_text="Ex: Venda de Animais, Venda de Produção, etc."
    )
    
    # Cliente (se aplicável)
    cliente = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Cliente"
    )
    
    # Valores e Datas
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor (R$)"
    )
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_recebimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Recebimento"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name="Status"
    )
    
    # Forma de Recebimento
    forma_recebimento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Forma de Recebimento"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ['data_vencimento', 'status']
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} - {self.data_vencimento}"
    
    def save(self, *args, **kwargs):
        # Atualizar status baseado na data
        from datetime import date
        if not self.data_recebimento:
            if self.data_vencimento < date.today():
                self.status = 'VENCIDA'
            else:
                self.status = 'PENDENTE'
        else:
            self.status = 'RECEBIDA'
        super().save(*args, **kwargs)


