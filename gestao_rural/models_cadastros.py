# -*- coding: utf-8 -*-
"""
Módulo Centralizado de Cadastros Master
Baseado na filosofia do Gestão Click - Inter-relação de Cadastros

Cadastros Disponíveis:
- UnidadeMedida: Unidades de medida padronizadas (kg, litros, unidades, etc.)
- Cliente: Cadastro de clientes
- Frigorifico: Cadastro de frigoríficos
- Fornecedor: Melhorado com inter-relações
- CentroCusto: Já existe mas será melhorado
- PlanoConta: Já existe mas será melhorado
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from .models import Propriedade


class TimeStampedModel(models.Model):
    """Modelo base com timestamps"""
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)
    
    class Meta:
        abstract = True


# ============================================================================
# UNIDADE DE MEDIDA (Cadastro Master)
# ============================================================================

class UnidadeMedida(TimeStampedModel):
    """Cadastro centralizado de unidades de medida"""
    TIPO_CHOICES = [
        ('PESO', 'Peso'),
        ('VOLUME', 'Volume'),
        ('COMPRIMENTO', 'Comprimento'),
        ('AREA', 'Área'),
        ('UNIDADE', 'Unidade'),
        ('TEMPO', 'Tempo'),
        ('ENERGIA', 'Energia'),
    ]
    
    codigo = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Código",
        help_text="Ex: KG, L, UN, HA"
    )
    nome = models.CharField(
        max_length=100,
        verbose_name="Nome Completo",
        help_text="Ex: Quilograma, Litro, Unidade"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo"
    )
    simbolo = models.CharField(
        max_length=10,
        verbose_name="Símbolo",
        help_text="Ex: kg, L, un"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição"
    )
    fator_conversao_padrao = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        default=Decimal('1.000000'),
        verbose_name="Fator de Conversão Padrão",
        help_text="Fator para conversão para unidade base do tipo"
    )
    unidade_base = models.BooleanField(
        default=False,
        verbose_name="É Unidade Base?",
        help_text="Marca se esta é a unidade base do tipo"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    ordem_exibicao = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem de Exibição"
    )
    
    class Meta:
        verbose_name = "Unidade de Medida"
        verbose_name_plural = "Unidades de Medida"
        ordering = ['tipo', 'ordem_exibicao', 'nome']
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['tipo', 'ativo']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.unidade_base and not self.fator_conversao_padrao == Decimal('1.000000'):
            raise ValidationError("Unidades base devem ter fator de conversão = 1.0")
    
    @classmethod
    def get_unidade_padrao(cls, tipo):
        """Retorna a unidade base de um tipo"""
        return cls.objects.filter(tipo=tipo, unidade_base=True, ativo=True).first()


# ============================================================================
# CLIENTE (Cadastro Master)
# ============================================================================

class Cliente(TimeStampedModel):
    """Cadastro centralizado de clientes"""
    TIPO_PESSOA_CHOICES = [
        ('FISICA', 'Pessoa Física'),
        ('JURIDICA', 'Pessoa Jurídica'),
    ]
    
    TIPO_CLIENTE_CHOICES = [
        ('FRIGORIFICO', 'Frigorífico'),
        ('FEIRANTE', 'Feirante'),
        ('ATACADISTA', 'Atacadista'),
        ('VAREJISTA', 'Varejista'),
        ('CONSUMIDOR_FINAL', 'Consumidor Final'),
        ('OUTROS', 'Outros'),
    ]
    
    # Propriedade (opcional - pode ser compartilhado entre propriedades)
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='clientes',
        null=True,
        blank=True,
        verbose_name="Propriedade",
        help_text="Quando vazio, cliente fica disponível para todas as propriedades"
    )
    
    # Dados Principais
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome/Razão Social"
    )
    nome_fantasia = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nome Fantasia"
    )
    tipo_pessoa = models.CharField(
        max_length=10,
        choices=TIPO_PESSOA_CHOICES,
        default='JURIDICA',
        verbose_name="Tipo de Pessoa"
    )
    cpf_cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CPF/CNPJ"
    )
    inscricao_estadual = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Inscrição Estadual"
    )
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE_CHOICES,
        default='OUTROS',
        verbose_name="Tipo de Cliente"
    )
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    
    # Endereço
    endereco = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    numero = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado (UF)")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    
    # Dados Bancários
    banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco")
    agencia = models.CharField(max_length=10, blank=True, null=True, verbose_name="Agência")
    conta = models.CharField(max_length=20, blank=True, null=True, verbose_name="Conta")
    tipo_conta = models.CharField(
        max_length=10,
        choices=[('CORRENTE', 'Corrente'), ('POUPANCA', 'Poupança')],
        blank=True,
        null=True,
        verbose_name="Tipo de Conta"
    )
    pix = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chave PIX")
    
    # Relacionamento com Frigorífico (se aplicável)
    frigorifico_vinculado = models.ForeignKey(
        'Frigorifico',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes_vinculados',
        verbose_name="Frigorífico Vinculado",
        help_text="Se este cliente é um frigorífico ou está vinculado a um"
    )
    
    # Status e Avaliação
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Avaliação (0-5)",
        help_text="Avaliação do cliente"
    )
    
    # Observações e Histórico
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    limite_credito = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Limite de Crédito (R$)"
    )
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['cpf_cnpj']),
            models.Index(fields=['tipo_cliente', 'ativo']),
            models.Index(fields=['propriedade', 'ativo']),
        ]
    
    def __str__(self):
        fantasia = f" ({self.nome_fantasia})" if self.nome_fantasia else ""
        return f"{self.nome}{fantasia}"
    
    @property
    def endereco_completo(self):
        """Retorna endereço formatado"""
        partes = [self.endereco]
        if self.numero:
            partes.append(f", {self.numero}")
        if self.complemento:
            partes.append(f" - {self.complemento}")
        if self.bairro:
            partes.append(f", {self.bairro}")
        if self.cidade:
            partes.append(f" - {self.cidade}")
        if self.estado:
            partes.append(f"/{self.estado}")
        if self.cep:
            partes.append(f" - CEP: {self.cep}")
        return "".join(partes) if any(partes) else ""


# ============================================================================
# FRIGORÍFICO (Cadastro Master)
# ============================================================================

class Frigorifico(TimeStampedModel):
    """Cadastro centralizado de frigoríficos"""
    TIPO_FRIGORIFICO_CHOICES = [
        ('ABATE', 'Abate'),
        ('ABATE_INDUSTRIALIZACAO', 'Abate e Industrialização'),
        ('INDUSTRIALIZACAO', 'Industrialização'),
        ('DISTRIBUIDOR', 'Distribuidor'),
    ]
    
    # Propriedade (opcional - pode ser compartilhado)
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='frigorificos',
        null=True,
        blank=True,
        verbose_name="Propriedade",
        help_text="Quando vazio, frigorífico fica disponível para todas as propriedades"
    )
    
    # Dados Principais
    razao_social = models.CharField(
        max_length=200,
        verbose_name="Razão Social"
    )
    nome_fantasia = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nome Fantasia"
    )
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name="CNPJ"
    )
    inscricao_estadual = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Inscrição Estadual"
    )
    tipo_frigorifico = models.CharField(
        max_length=30,
        choices=TIPO_FRIGORIFICO_CHOICES,
        default='ABATE',
        verbose_name="Tipo de Frigorífico"
    )
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    
    # Endereço
    endereco = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    numero = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado (UF)")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    
    # Dados Bancários
    banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco")
    agencia = models.CharField(max_length=10, blank=True, null=True, verbose_name="Agência")
    conta = models.CharField(max_length=20, blank=True, null=True, verbose_name="Conta")
    tipo_conta = models.CharField(
        max_length=10,
        choices=[('CORRENTE', 'Corrente'), ('POUPANCA', 'Poupança')],
        blank=True,
        null=True,
        verbose_name="Tipo de Conta"
    )
    pix = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chave PIX")
    
    # Dados Específicos do Frigorífico
    capacidade_abate_dia = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Capacidade de Abate (cabeças/dia)"
    )
    servico_inspecao = models.CharField(
        max_length=50,
        choices=[
            ('SIF', 'SIF - Serviço de Inspeção Federal'),
            ('SIM', 'SIM - Serviço de Inspeção Municipal'),
            ('SIE', 'SIE - Serviço de Inspeção Estadual'),
        ],
        blank=True,
        null=True,
        verbose_name="Serviço de Inspeção"
    )
    numero_inspecao = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número do Certificado de Inspeção"
    )
    
    # Condições Comerciais
    prazo_pagamento_dias = models.PositiveIntegerField(
        default=30,
        verbose_name="Prazo de Pagamento (dias)"
    )
    desconto_padrao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Desconto Padrão (%)"
    )
    
    # Status e Avaliação
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Avaliação (0-5)",
        help_text="Avaliação do frigorífico"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Criado por
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='frigorificos_criados',
        verbose_name="Criado por"
    )
    
    class Meta:
        verbose_name = "Frigorífico"
        verbose_name_plural = "Frigoríficos"
        ordering = ['razao_social']
        indexes = [
            models.Index(fields=['cnpj']),
            models.Index(fields=['tipo_frigorifico', 'ativo']),
            models.Index(fields=['propriedade', 'ativo']),
        ]
    
    def __str__(self):
        fantasia = f" ({self.nome_fantasia})" if self.nome_fantasia else ""
        return f"{self.razao_social}{fantasia}"
    
    @property
    def endereco_completo(self):
        """Retorna endereço formatado"""
        partes = [self.endereco]
        if self.numero:
            partes.append(f", {self.numero}")
        if self.complemento:
            partes.append(f" - {self.complemento}")
        if self.bairro:
            partes.append(f", {self.bairro}")
        if self.cidade:
            partes.append(f" - {self.cidade}")
        if self.estado:
            partes.append(f"/{self.estado}")
        if self.cep:
            partes.append(f" - CEP: {self.cep}")
        return "".join(partes) if any(partes) else ""


# ============================================================================
# FORNECEDOR MELHORADO (Integração com outros cadastros)
# ============================================================================

class FornecedorCadastro(TimeStampedModel):
    """Cadastro melhorado de fornecedores com inter-relações"""
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
    
    # Propriedade (opcional - pode ser compartilhado)
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='fornecedores_master',
        null=True,
        blank=True,
        verbose_name="Propriedade",
        help_text="Quando vazio, fornecedor fica disponível para todas as propriedades"
    )
    
    # Dados Principais
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
    inscricao_estadual = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Inscrição Estadual"
    )
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    
    # Endereço
    endereco = models.CharField(max_length=255, blank=True, null=True, verbose_name="Logradouro")
    numero = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado (UF)")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    
    # Dados Bancários
    banco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banco")
    agencia = models.CharField(max_length=10, blank=True, null=True, verbose_name="Agência")
    conta = models.CharField(max_length=20, blank=True, null=True, verbose_name="Conta")
    tipo_conta = models.CharField(
        max_length=10,
        choices=[('CORRENTE', 'Corrente'), ('POUPANCA', 'Poupança')],
        blank=True,
        null=True,
        verbose_name="Tipo de Conta"
    )
    pix = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chave PIX")
    
    # Relacionamento com Centro de Custo e Plano de Contas
    centro_custo_padrao = models.ForeignKey(
        'CentroCusto',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fornecedores_cadastro',
        verbose_name="Centro de Custo Padrão"
    )
    plano_conta_padrao = models.ForeignKey(
        'PlanoConta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fornecedores_cadastro',
        verbose_name="Plano de Contas Padrão"
    )
    
    # Condições Comerciais
    prazo_pagamento_dias = models.PositiveIntegerField(
        default=30,
        verbose_name="Prazo de Pagamento Padrão (dias)"
    )
    desconto_padrao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Desconto Padrão (%)"
    )
    
    # Status e Avaliação
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Avaliação (0-5)",
        help_text="Avaliação do fornecedor"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Criado por
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fornecedores_criados',
        verbose_name="Criado por"
    )
    
    class Meta:
        verbose_name = "Fornecedor Cadastro"
        verbose_name_plural = "Fornecedores Cadastro"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['cpf_cnpj']),
            models.Index(fields=['tipo', 'ativo']),
            models.Index(fields=['propriedade', 'ativo']),
        ]
    
    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"
    
    @property
    def endereco_completo(self):
        """Retorna endereço formatado"""
        partes = [self.endereco]
        if self.numero:
            partes.append(f", {self.numero}")
        if self.complemento:
            partes.append(f" - {self.complemento}")
        if self.bairro:
            partes.append(f", {self.bairro}")
        if self.cidade:
            partes.append(f" - {self.cidade}")
        if self.estado:
            partes.append(f"/{self.estado}")
        if self.cep:
            partes.append(f" - CEP: {self.cep}")
        return "".join(partes) if any(partes) else ""


# ============================================================================
# RELACIONAMENTOS ENTRE CADASTROS
# ============================================================================

class RelacionamentoCadastros(TimeStampedModel):
    """Tabela para relacionar cadastros entre si"""
    TIPO_RELACIONAMENTO_CHOICES = [
        ('FORNECEDOR_CLIENTE', 'Fornecedor também é Cliente'),
        ('CLIENTE_FRIGORIFICO', 'Cliente é Frigorífico'),
        ('FORNECEDOR_FRIGORIFICO', 'Fornecedor é Frigorífico'),
        ('GRUPO_EMPRESARIAL', 'Grupo Empresarial'),
        ('OUTROS', 'Outros'),
    ]
    
    tipo_relacionamento = models.CharField(
        max_length=30,
        choices=TIPO_RELACIONAMENTO_CHOICES,
        verbose_name="Tipo de Relacionamento"
    )
    
    # Relacionamentos flexíveis
    fornecedor = models.ForeignKey(
        'FornecedorCadastro',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='relacionamentos_fornecedor',
        verbose_name="Fornecedor"
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='relacionamentos_cliente',
        verbose_name="Cliente"
    )
    frigorifico = models.ForeignKey(
        Frigorifico,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='relacionamentos_frigorifico',
        verbose_name="Frigorífico"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Relacionamento entre Cadastros"
        verbose_name_plural = "Relacionamentos entre Cadastros"
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.get_tipo_relacionamento_display()} - {self.criado_em}"

