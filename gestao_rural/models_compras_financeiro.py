# -*- coding: utf-8 -*-
"""
Modelos para Módulo de Compras e Financeiro
Inclui: Fornecedores, Produtos, Notas Fiscais, Ordens de Compra, Contas a Pagar/Receber
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from .models import Propriedade


# ============================================================================
# FORNECEDOR
# ============================================================================

class Fornecedor(models.Model):
    """Cadastro de fornecedores"""
    TIPO_CHOICES = [
        ('RACAO', 'Ração/Insumos'),
        ('MEDICAMENTO', 'Medicamentos/Veterinário'),
        ('EQUIPAMENTO', 'Equipamentos'),
        ('COMBUSTIVEL', 'Combustível'),
        ('SERVICO', 'Serviços'),
        ('CONSTRUCAO', 'Construção'),
        ('TRANSPORTE', 'Transporte'),
        ('OUTROS', 'Outros'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='fornecedores',
        null=True,
        blank=True,
        verbose_name="Propriedade"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome/Razão Social")
    nome_fantasia = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nome Fantasia"
    )
    cpf_cnpj = models.CharField(max_length=18, verbose_name="CPF/CNPJ")
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='OUTROS',
        verbose_name="Tipo de Fornecedor"
    )
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True, verbose_name="Inscrição Estadual")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado (UF)")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco")
    agencia = models.CharField(max_length=20, blank=True, null=True, verbose_name="Agência")
    conta = models.CharField(max_length=30, blank=True, null=True, verbose_name="Conta")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


# ============================================================================
# PRODUTO E CATEGORIA
# ============================================================================

class CategoriaProduto(models.Model):
    """Categorias de produtos"""
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
    """Cadastro de produtos"""
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
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código do Produto")
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    categoria = models.ForeignKey(
        CategoriaProduto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria"
    )
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
        help_text="Nomenclatura Comum do Mercosul (ex: 0102.29.00) - OBRIGATÓRIO",
        blank=False,
        null=False
    )
    ncm_descricao = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Descrição do NCM"
    )
    
    # Origem da Mercadoria
    ORIGEM_CHOICES = [
        ('0', '0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8'),
        ('1', '1 - Estrangeira - Importação direta, exceto a indicada no código 6'),
        ('2', '2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7'),
        ('3', '3 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 40%'),
        ('4', '4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos'),
        ('5', '5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%'),
        ('6', '6 - Estrangeira - Importação direta, sem similar nacional'),
        ('7', '7 - Estrangeira - Adquirida no mercado interno, sem similar nacional'),
        ('8', '8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%'),
    ]
    origem_mercadoria = models.CharField(
        max_length=1,
        choices=ORIGEM_CHOICES,
        default='0',
        verbose_name="Origem da Mercadoria"
    )
    
    # Campos adicionais
    cest = models.CharField(max_length=7, blank=True, null=True, verbose_name="CEST")
    gtin = models.CharField(max_length=14, blank=True, null=True, verbose_name="GTIN/EAN")
    ex_tipi = models.CharField(max_length=3, blank=True, null=True, verbose_name="Exceção da TIPI")
    
    # CFOP
    cfop_entrada = models.CharField(max_length=10, blank=True, null=True, verbose_name="CFOP Entrada")
    cfop_saida_estadual = models.CharField(max_length=10, blank=True, null=True, verbose_name="CFOP Saída Estadual")
    cfop_saida_interestadual = models.CharField(max_length=10, blank=True, null=True, verbose_name="CFOP Saída Interestadual")
    
    # Descrição completa
    descricao_completa = models.TextField(blank=True, null=True, verbose_name="Descrição Completa")
    
    # Tributação
    cst_icms = models.CharField(max_length=3, blank=True, null=True, verbose_name="CST ICMS")
    aliquota_icms = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Alíquota ICMS (%)"
    )
    cst_ipi = models.CharField(max_length=3, blank=True, null=True, verbose_name="CST IPI")
    aliquota_ipi = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Alíquota IPI (%)"
    )
    cst_pis = models.CharField(max_length=3, blank=True, null=True, verbose_name="CST PIS")
    aliquota_pis = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Alíquota PIS (%)"
    )
    cst_cofins = models.CharField(max_length=3, blank=True, null=True, verbose_name="CST COFINS")
    aliquota_cofins = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Alíquota COFINS (%)"
    )
    
    # Preços
    preco_custo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Preço de Custo (R$)"
    )
    preco_venda = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Preço de Venda (R$)"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['descricao']
    
    def __str__(self):
        return f"{self.codigo} - {self.descricao}"
    
    def save(self, *args, **kwargs):
        """Override save para limpar e formatar campos fiscais"""
        # Formatar NCM (8 dígitos: XXXX.XX.XX)
        if self.ncm:
            ncm_limpo = self.ncm.replace('.', '').replace('-', '')
            if len(ncm_limpo) == 8:
                self.ncm = f"{ncm_limpo[:4]}.{ncm_limpo[4:6]}.{ncm_limpo[6:]}"
        super().save(*args, **kwargs)


# ============================================================================
# NOTA FISCAL
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
    data_cancelamento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Cancelamento"
    )
    justificativa_cancelamento = models.TextField(
        blank=True,
        null=True,
        verbose_name="Justificativa do Cancelamento",
        help_text="Justificativa obrigatória para cancelamento da NF-e (mínimo 15 caracteres)"
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
    ORIGEM_CHOICES = [
        ('0', '0 - Nacional, exceto as indicadas nos códigos 3, 4, 5 e 8'),
        ('1', '1 - Estrangeira - Importação direta, exceto a indicada no código 6'),
        ('2', '2 - Estrangeira - Adquirida no mercado interno, exceto a indicada no código 7'),
        ('3', '3 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 40%'),
        ('4', '4 - Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos'),
        ('5', '5 - Nacional, mercadoria ou bem com Conteúdo de Importação inferior ou igual a 40%'),
        ('6', '6 - Estrangeira - Importação direta, sem similar nacional'),
        ('7', '7 - Estrangeira - Adquirida no mercado interno, sem similar nacional'),
        ('8', '8 - Nacional, mercadoria ou bem com Conteúdo de Importação superior a 70%'),
    ]
    origem_mercadoria = models.CharField(
        max_length=1,
        choices=ORIGEM_CHOICES,
        default='0',
        verbose_name="Origem da Mercadoria",
        help_text="Origem da mercadoria conforme tabela da Receita Federal"
    )
    cest = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        verbose_name="CEST",
        help_text="Código Especificador da Substituição Tributária"
    )
    gtin = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name="GTIN/EAN",
        help_text="Código GTIN (EAN/UPC) do produto"
    )
    ex_tipi = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        verbose_name="Exceção da TIPI"
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
            if not self.origem_mercadoria:
                self.origem_mercadoria = self.produto.origem_mercadoria
            if not self.cest and self.produto.cest:
                self.cest = self.produto.cest
            if not self.gtin and self.produto.gtin:
                self.gtin = self.produto.gtin
            if not self.ex_tipi and self.produto.ex_tipi:
                self.ex_tipi = self.produto.ex_tipi
            if not self.unidade_medida:
                self.unidade_medida = self.produto.unidade_medida
            
            # Determinar CFOP baseado no tipo de nota e UF
            if self.nota_fiscal.tipo == 'ENTRADA' and self.produto.cfop_entrada:
                self.cfop = self.produto.cfop_entrada
            elif self.nota_fiscal.tipo == 'SAIDA':
                # Verificar se é interestadual
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
        
        # Calcular valor_total se não estiver definido
        if not self.valor_total or self.valor_total == 0:
            self.valor_total = self.quantidade * self.valor_unitario
        
        super().save(*args, **kwargs)


# ============================================================================
# NUMERAÇÃO SEQUENCIAL DE NF-E (NOVO MODELO)
# ============================================================================

class NumeroSequencialNFE(models.Model):
    """
    Controla a numeração sequencial de NF-e por propriedade e série
    Conforme legislação fiscal, cada estabelecimento deve ter numeração única por série
    """
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='numeros_sequenciais_nfe',
        verbose_name="Propriedade"
    )
    serie = models.CharField(
        max_length=10,
        default='1',
        verbose_name="Série da NF-e",
        help_text="Série da nota fiscal (geralmente '1' para a série normal)"
    )
    proximo_numero = models.IntegerField(
        default=1,
        verbose_name="Próximo Número",
        help_text="Próximo número sequencial a ser usado nesta série"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data da Última Atualização"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações",
        help_text="Observações sobre esta série (ex: 'Série normal', 'Série de teste', etc.)"
    )

    class Meta:
        verbose_name = "Número Sequencial de NF-e"
        verbose_name_plural = "Números Sequenciais de NF-e"
        unique_together = [['propriedade', 'serie']]
        ordering = ['propriedade', 'serie']

    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - Série {self.serie} - Próximo: {self.proximo_numero}"
    
    def obter_proximo_numero(self):
        """
        Retorna o próximo número e incrementa o contador
        """
        numero = self.proximo_numero
        self.proximo_numero += 1
        self.save(update_fields=['proximo_numero', 'data_atualizacao'])
        return numero

    @classmethod
    def obter_ou_criar(cls, propriedade, serie='1'):
        """
        Obtém ou cria um registro de numeração sequencial para a propriedade e série
        """
        obj, created = cls.objects.get_or_create(
                    propriedade=propriedade,
            serie=serie,
            defaults={'proximo_numero': 1}
        )
        return obj


# ============================================================================
# ORDEM DE COMPRA (Stubs - para não quebrar imports existentes)
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
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='ordens_compra',
        verbose_name="Propriedade"
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='ordens_compra',
        verbose_name="Fornecedor"
    )
    nota_fiscal = models.ForeignKey(
        NotaFiscal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Nota Fiscal"
    )
    requisicao_origem = models.ForeignKey(
        'RequisicaoCompra',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ordens_geradas',
        verbose_name='Requisição de Origem'
    )
    setor = models.ForeignKey(
        'SetorPropriedade',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ordens_compra',
        verbose_name='Setor Responsável'
    )
    centro_custo = models.ForeignKey(
        'CentroCusto',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ordens_compra',
        verbose_name='Centro de Custo'
    )
    centro_custo_descricao = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name='Centro de Custo (Manual)'
    )
    plano_conta = models.ForeignKey(
        'PlanoConta',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ordens_compra',
        verbose_name='Plano de Contas'
    )
    numero_ordem = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Número da Ordem'
    )
    data_emissao = models.DateField(
        verbose_name='Data de Emissão'
    )
    data_entrega_prevista = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Entrega Prevista'
    )
    data_recebimento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Recebimento'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name="Status"
    )
    valor_produtos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor dos Produtos (R$)'
    )
    valor_frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Valor do Frete (R$)'
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Total (R$)"
    )
    condicoes_pagamento = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Condições de Pagamento'
    )
    forma_pagamento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Forma de Pagamento'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    data_aprovacao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Aprovação'
    )
    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ordens_compra_aprovadas',
        verbose_name='Aprovado por'
    )
    autorizacao_setor_status = models.CharField(
        max_length=15,
        choices=[
            ('PENDENTE', 'Pendente'),
            ('AUTORIZADA', 'Autorizada'),
            ('NEGADA', 'Negada'),
        ],
        default='PENDENTE',
        verbose_name='Status Autorização Setor'
    )
    autorizacao_setor_usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ordens_compra_autorizadas_setor',
        verbose_name='Responsável Autorização Setor'
    )
    autorizacao_setor_data = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data Autorização Setor'
    )
    autorizacao_setor_observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações da Autorização do Setor'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ordens_compra_criadas',
        verbose_name='Criado por'
    )
    
    class Meta:
        verbose_name = "Ordem de Compra"
        verbose_name_plural = "Ordens de Compra"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"OC {self.numero_ordem}"
    
    def __str__(self):
        return f"OC {self.numero}"


class ItemOrdemCompra(models.Model):
    """Item de Ordem de Compra - Stub básico"""
    ordem_compra = models.ForeignKey(OrdemCompra, on_delete=models.CASCADE, related_name='itens')
    
    class Meta:
        verbose_name = "Item de Ordem de Compra"
        verbose_name_plural = "Itens de Ordem de Compra"
    
    def __str__(self):
        return f"Item {self.id}"


# ============================================================================
# CONTAS A PAGAR/RECEBER (Stubs - para não quebrar imports existentes)
# ============================================================================

class ContaPagar(models.Model):
    """Conta a Pagar"""
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
        verbose_name='Propriedade'
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contas_pagar',
        verbose_name='Fornecedor'
    )
    ordem_compra = models.ForeignKey(
        'OrdemCompra',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contas_pagar',
        verbose_name='Ordem de Compra'
    )
    nota_fiscal = models.ForeignKey(
        NotaFiscal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contas_pagar',
        verbose_name='Nota Fiscal'
    )
    descricao = models.CharField(
        max_length=200,
        verbose_name='Descrição'
    )
    categoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Ex: Combustível, Ração, Salário, etc.',
        verbose_name='Categoria'
    )
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor (R$)'
    )
    data_vencimento = models.DateField(
        verbose_name='Data de Vencimento'
    )
    data_pagamento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Pagamento'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    forma_pagamento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Forma de Pagamento'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    data_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Registro'
    )

    class Meta:
        verbose_name = "Conta a Pagar"
        verbose_name_plural = "Contas a Pagar"
        ordering = ['data_vencimento', 'status']

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"


class ContaReceber(models.Model):
    """Conta a Receber"""
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
        verbose_name='Propriedade'
    )
    descricao = models.CharField(
        max_length=200,
        verbose_name='Descrição'
    )
    categoria = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Ex: Venda de Animais, Venda de Produção, etc.',
        verbose_name='Categoria'
    )
    cliente = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Cliente'
    )
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor (R$)'
    )
    data_vencimento = models.DateField(
        verbose_name='Data de Vencimento'
    )
    data_recebimento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Recebimento'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    forma_recebimento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Forma de Recebimento'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    data_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Registro'
    )
    
    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ['data_vencimento', 'status']
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor}"


# Stubs adicionais para outros imports que possam existir
class RequisicaoCompra(models.Model):
    """Requisição de compra de insumos"""
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
        verbose_name='Propriedade'
    )
    solicitante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='requisicoes_compra_criadas',
        verbose_name='Solicitante'
    )
    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name='Status'
    )
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='MEDIA',
        verbose_name='Prioridade'
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    justificativa = models.TextField(
        verbose_name='Justificativa'
    )
    data_necessidade = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Necessidade'
    )
    centro_custo = models.ForeignKey(
        'CentroCusto',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='requisicoes_compra',
        verbose_name='Centro de Custo'
    )
    centro_custo_descricao = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name='Centro de Custo (Manual)'
    )
    plano_conta = models.ForeignKey(
        'PlanoConta',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='requisicoes_compra',
        verbose_name='Plano de Contas'
    )
    setor = models.ForeignKey(
        'SetorPropriedade',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='requisicoes',
        verbose_name='Setor Solicitante'
    )
    equipamento = models.ForeignKey(
        'Equipamento',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='requisicoes_compra',
        verbose_name='Máquina/Equipamento'
    )
    ordem_compra = models.ForeignKey(
        'OrdemCompra',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='requisicoes_origem',
        verbose_name='Ordem de Compra Gerada'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    motivo_cancelamento = models.TextField(
        blank=True,
        null=True,
        verbose_name='Motivo do Cancelamento'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    enviado_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Envio'
    )
    concluido_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de Conclusão'
    )
    
    class Meta:
        verbose_name = 'Requisição de Compra'
        verbose_name_plural = 'Requisições de Compra'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"RC {self.id}"


class ItemRequisicaoCompra(models.Model):
    """Item de uma requisição de compra"""
    UNIDADE_MEDIDA_CHOICES = [
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
        verbose_name='Requisição'
    )
    descricao = models.CharField(
        max_length=255,
        verbose_name='Descrição do Item'
    )
    unidade_medida = models.CharField(
        max_length=10,
        choices=UNIDADE_MEDIDA_CHOICES,
        default='UN',
        verbose_name='Unidade de Medida'
    )
    quantidade = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='Quantidade'
    )
    valor_estimado_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Estimado Unitário (R$)'
    )
    fornecedor_preferencial = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Fornecedor Preferencial'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações do Item'
    )
    
    class Meta:
        verbose_name = 'Item de Requisição de Compra'
        verbose_name_plural = 'Itens de Requisição de Compra'
        ordering = ['requisicao', 'descricao']
    
    def __str__(self):
        return f"Item {self.id}"
    
    @property
    def valor_estimado_total(self):
        """Calcula o valor total estimado do item"""
        if self.quantidade and self.valor_estimado_unitario:
            return self.quantidade * self.valor_estimado_unitario
        return Decimal('0.00')


class AprovacaoRequisicaoCompra(models.Model):
    """Aprovação de uma requisição de compra em diferentes etapas"""
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
        verbose_name='Requisição'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='aprovacoes_requisicao',
        verbose_name='Usuário'
    )
    etapa = models.CharField(
        max_length=30,
        choices=ETAPA_CHOICES,
        verbose_name='Etapa'
    )
    decisao = models.CharField(
        max_length=20,
        choices=DECISAO_CHOICES,
        default='PENDENTE',
        verbose_name='Decisão'
    )
    comentario = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentário'
    )
    data_decisao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data da Decisão'
    )
    
    class Meta:
        verbose_name = 'Aprovação de Requisição'
        verbose_name_plural = 'Aprovações de Requisição'
        ordering = ['-data_decisao']
    
    def __str__(self):
        return f"Aprovação {self.id}"


class CotacaoFornecedor(models.Model):
    """Cotação de preços fornecida por um fornecedor"""
    STATUS_CHOICES = [
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('RECEBIDA', 'Recebida'),
        ('SELECIONADA', 'Selecionada'),
        ('NAO_SELECIONADA', 'Não Selecionada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='cotacoes',
        verbose_name='Fornecedor'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EM_ANDAMENTO',
        verbose_name='Status'
    )
    prazo_entrega_estimado = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name='Prazo de Entrega Estimado'
    )
    validade_proposta = models.DateField(
        blank=True,
        null=True,
        verbose_name='Validade da Proposta'
    )
    condicoes_pagamento = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Condições de Pagamento'
    )
    valor_frete = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor do Frete (R$)'
    )
    valor_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Total Cotado (R$)'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    anexo_proposta = models.FileField(
        upload_to='compras/cotacoes/',
        blank=True,
        null=True,
        verbose_name='Proposta Anexada'
    )
    comprador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cotacoes_registradas',
        verbose_name='Comprador Responsável'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Registro'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Cotação de Fornecedor'
        verbose_name_plural = 'Cotações de Fornecedores'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Cotação {self.id}"


class ItemCotacaoFornecedor(models.Model):
    """Item de uma cotação de fornecedor"""
    cotacao = models.ForeignKey(
        CotacaoFornecedor,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Cotação'
    )
    item_requisicao = models.ForeignKey(
        'ItemRequisicaoCompra',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='itens_cotados',
        verbose_name='Item da Requisição'
    )
    descricao = models.CharField(
        max_length=255,
        verbose_name='Descrição'
    )
    unidade_medida = models.CharField(
        max_length=10,
        default='UN',
        verbose_name='Unidade'
    )
    quantidade = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
        verbose_name='Quantidade'
    )
    valor_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Valor Unitário (R$)'
    )
    valor_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor Total (R$)'
    )
    
    class Meta:
        verbose_name = 'Item de Cotação'
        verbose_name_plural = 'Itens de Cotação'
        ordering = ['cotacao', 'descricao']
    
    def __str__(self):
        return f"Item {self.id}"
    
    def save(self, *args, **kwargs):
        """Calcula o valor total automaticamente"""
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)


class RecebimentoCompra(models.Model):
    """Recebimento de uma ordem de compra"""
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('RECEBIDO', 'Recebido'),
        ('DIVERGENCIA', 'Divergência'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    ordem_compra = models.ForeignKey(
        OrdemCompra,
        on_delete=models.CASCADE,
        related_name='recebimentos',
        verbose_name='Ordem de Compra'
    )
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='recebimentos_registrados',
        verbose_name='Responsável Pelo Recebimento'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status'
    )
    data_prevista = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data Prevista'
    )
    data_recebimento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Data de Recebimento'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    comprovante_assinado = models.FileField(
        upload_to='compras/recebimentos/',
        blank=True,
        null=True,
        verbose_name='Comprovante Assinado'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Registro'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Recebimento de Compra'
        verbose_name_plural = 'Recebimentos de Compra'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Recebimento {self.id}"


class ItemRecebimentoCompra(models.Model):
    """Item recebido de uma ordem de compra"""
    recebimento = models.ForeignKey(
        RecebimentoCompra,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Recebimento'
    )
    item_ordem = models.ForeignKey(
        'ItemOrdemCompra',
        on_delete=models.CASCADE,
        related_name='recebimentos',
        verbose_name='Item da Ordem'
    )
    quantidade_recebida = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.000'))],
        verbose_name='Quantidade Recebida'
    )
    divergencia = models.BooleanField(
        default=False,
        verbose_name='Possui Divergência?'
    )
    justificativa_divergencia = models.TextField(
        blank=True,
        null=True,
        verbose_name='Justificativa da Divergência'
    )
    
    class Meta:
        verbose_name = 'Item Recebido'
        verbose_name_plural = 'Itens Recebidos'
        ordering = ['recebimento', 'item_ordem']
    
    def __str__(self):
        return f"Item {self.id}"


class SetorPropriedade(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    class Meta:
        verbose_name = "Setor da Propriedade"
    def __str__(self):
        return self.nome


class ConviteCotacaoFornecedor(models.Model):
    """Convite de cotação enviado para fornecedor"""
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
        verbose_name="Requisição"
    )
    fornecedor = models.ForeignKey(
        Fornecedor,
        on_delete=models.CASCADE,
        related_name='convites_cotacao',
        verbose_name="Fornecedor"
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
    enviado_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Data de envio'
    )
    data_expiracao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Expira em'
    )
    respondido_em = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Respondido em'
    )
    observacao_resposta = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações do fornecedor'
    )
    enviado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='convites_cotacao_enviados',
        verbose_name='Criado por'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    class Meta:
        verbose_name = "Convite de Cotação"
        verbose_name_plural = "Convites de Cotação"
        ordering = ['-criado_em']
        constraints = [
            models.UniqueConstraint(
                fields=['requisicao', 'fornecedor'],
                name='unique_convite_requisicao_fornecedor'
            )
        ]
    
    def __str__(self):
        return f"Convite {self.id}"
    
    def save(self, *args, **kwargs):
        """Gera token automaticamente se não existir"""
        import secrets
        if not self.token:
            self.token = secrets.token_urlsafe(24)[:32]
        super().save(*args, **kwargs)


class OrcamentoCompraMensal(models.Model):
    """Orçamento mensal de compras por setor"""
    MES_CHOICES = [
        (1, 'Janeiro'),
        (2, 'Fevereiro'),
        (3, 'Março'),
        (4, 'Abril'),
        (5, 'Maio'),
        (6, 'Junho'),
        (7, 'Julho'),
        (8, 'Agosto'),
        (9, 'Setembro'),
        (10, 'Outubro'),
        (11, 'Novembro'),
        (12, 'Dezembro'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='orcamentos_compras',
        verbose_name='Propriedade'
    )
    setor = models.ForeignKey(
        'SetorPropriedade',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orcamentos_mensais',
        verbose_name='Setor'
    )
    ano = models.PositiveIntegerField(
        verbose_name='Ano'
    )
    mes = models.PositiveSmallIntegerField(
        choices=MES_CHOICES,
        verbose_name='Mês'
    )
    valor_limite = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Limite Mensal (R$)'
    )
    limite_extra = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Limite Extra (R$)'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observações'
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orcamentos_compras_criados',
        verbose_name='Criado por'
    )
    atualizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='orcamentos_compras_atualizados',
        verbose_name='Atualizado por'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    
    class Meta:
        verbose_name = 'Orçamento Mensal de Compras'
        verbose_name_plural = 'Orçamentos Mensais de Compras'
        ordering = ['-ano', '-mes', 'setor__nome']
        unique_together = [('propriedade', 'setor', 'ano', 'mes')]
    
    def __str__(self):
        setor_nome = self.setor.nome if self.setor else "Geral"
        mes_nome = dict(self.MES_CHOICES).get(self.mes, str(self.mes))
        return f"{setor_nome} - {mes_nome}/{self.ano}"


class AjusteOrcamentoCompra(models.Model):
    """Ajuste emergencial de orçamento mensal"""
    orcamento = models.ForeignKey(
        OrcamentoCompraMensal,
        on_delete=models.CASCADE,
        related_name='ajustes',
        verbose_name='Orçamento'
    )
    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Informe o valor adicional aprovado para este mês.',
        verbose_name='Valor do Ajuste (R$)'
    )
    justificativa = models.TextField(
        verbose_name='Justificativa do ajuste'
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ajustes_orcamento_criados',
        verbose_name='Criado por'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    
    class Meta:
        verbose_name = 'Ajuste Emergencial de Orçamento'
        verbose_name_plural = 'Ajustes Emergenciais de Orçamento'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Ajuste de R$ {self.valor} - {self.orcamento}"


class AutorizacaoExcedenteOrcamento(models.Model):
    orcamento = models.ForeignKey(OrcamentoCompraMensal, on_delete=models.CASCADE)
    class Meta:
        verbose_name = "Autorização de Excedente de Orçamento"
    def __str__(self):
        return f"Autorização {self.id}"


class EventoFluxoCompra(models.Model):
    requisicao = models.ForeignKey(RequisicaoCompra, on_delete=models.CASCADE)
    class Meta:
        verbose_name = "Evento de Fluxo de Compra"
    def __str__(self):
        return f"Evento {self.id}"

