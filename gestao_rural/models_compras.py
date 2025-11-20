# -*- coding: utf-8 -*-
"""
Modelos para Módulo de Compras de Insumos
Baseado em: iRancho, Caviúna, Prodap Views
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from .models import Propriedade


class Fornecedor(models.Model):
    """Cadastro de fornecedores"""
    TIPO_FORNECEDOR_CHOICES = [
        ('RACAO', 'Ração'),
        ('MEDICAMENTO', 'Medicamento'),
        ('SUPLEMENTO', 'Suplemento'),
        ('EQUIPAMENTO', 'Equipamento'),
        ('ANIMAIS', 'Animais'),
        ('SERVICOS', 'Serviços'),
        ('OUTROS', 'Outros'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome/Razão Social")
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    tipo_fornecedor = models.CharField(
        max_length=20,
        choices=TIPO_FORNECEDOR_CHOICES,
        verbose_name="Tipo de Fornecedor"
    )
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    contato_responsavel = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Contato Responsável"
    )
    avaliacao = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Avaliação (0-5)",
        help_text="Avaliação do fornecedor de 0 a 5"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class CategoriaInsumo(models.Model):
    """Categorias de insumos"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Categoria de Insumo"
        verbose_name_plural = "Categorias de Insumos"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Insumo(models.Model):
    """Catálogo de insumos"""
    UNIDADE_MEDIDA_CHOICES = [
        ('KG', 'Quilograma (kg)'),
        ('TON', 'Tonelada (t)'),
        ('L', 'Litro (L)'),
        ('UN', 'Unidade'),
        ('SC', 'Saca (sc)'),
        ('CX', 'Caixa'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome do Insumo")
    categoria = models.ForeignKey(
        CategoriaInsumo,
        on_delete=models.CASCADE,
        verbose_name="Categoria"
    )
    unidade_medida = models.CharField(
        max_length=10,
        choices=UNIDADE_MEDIDA_CHOICES,
        default='KG',
        verbose_name="Unidade de Medida"
    )
    fornecedor_principal = models.ForeignKey(
        Fornecedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='insumos',
        verbose_name="Fornecedor Principal"
    )
    preco_medio_mercado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Preço Médio de Mercado (R$)"
    )
    preco_ultima_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Preço da Última Compra (R$)"
    )
    data_ultima_compra = models.DateField(null=True, blank=True, verbose_name="Data da Última Compra")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['categoria', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_unidade_medida_display()})"


class EstoqueInsumo(models.Model):
    """Estoque de insumos por propriedade"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='estoques_insumos',
        verbose_name="Propriedade"
    )
    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        related_name='estoques',
        verbose_name="Insumo"
    )
    quantidade_atual = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name="Quantidade Atual"
    )
    quantidade_minima = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name="Quantidade Mínima",
        help_text="Alerta quando estoque ficar abaixo deste valor"
    )
    quantidade_maxima = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name="Quantidade Máxima"
    )
    valor_unitario_medio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Unitário Médio (R$)"
    )
    valor_total_estoque = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Total do Estoque (R$)"
    )
    data_ultima_entrada = models.DateField(null=True, blank=True, verbose_name="Data da Última Entrada")
    data_ultima_saida = models.DateField(null=True, blank=True, verbose_name="Data da Última Saída")
    data_validade = models.DateField(null=True, blank=True, verbose_name="Data de Validade")
    localizacao = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Localização",
        help_text="Depósito, Galpão, etc."
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Estoque de Insumo"
        verbose_name_plural = "Estoques de Insumos"
        unique_together = ['propriedade', 'insumo']
        ordering = ['insumo__categoria', 'insumo__nome']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.insumo.nome}: {self.quantidade_atual} {self.insumo.get_unidade_medida_display()}"
    
    @property
    def estoque_baixo(self):
        """Verifica se estoque está abaixo do mínimo"""
        return self.quantidade_atual < self.quantidade_minima if self.quantidade_minima > 0 else False
    
    @property
    def percentual_estoque(self):
        """Calcula percentual de estoque em relação ao máximo"""
        if self.quantidade_maxima > 0:
            return (self.quantidade_atual / self.quantidade_maxima) * 100
        return 0


class OrdemCompra(models.Model):
    """Ordem de compra de insumos"""
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
    numero_ordem = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número da Ordem"
    )
    data_emissao = models.DateField(verbose_name="Data de Emissão")
    data_entrega_prevista = models.DateField(verbose_name="Data de Entrega Prevista")
    data_recebimento = models.DateField(null=True, blank=True, verbose_name="Data de Recebimento")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name="Status"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor Total (R$)"
    )
    valor_frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor do Frete (R$)"
    )
    condicoes_pagamento = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Condições de Pagamento"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    aprovado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_aprovadas',
        verbose_name="Aprovado por"
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aprovação")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Ordem de Compra"
        verbose_name_plural = "Ordens de Compra"
        ordering = ['-data_emissao', '-numero_ordem']
    
    def __str__(self):
        return f"OC {self.numero_ordem} - {self.fornecedor.nome}"


class ItemOrdemCompra(models.Model):
    """Itens da ordem de compra"""
    ordem_compra = models.ForeignKey(
        OrdemCompra,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Ordem de Compra"
    )
    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        verbose_name="Insumo"
    )
    quantidade_solicitada = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="Quantidade Solicitada"
    )
    quantidade_recebida = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal('0.000'),
        verbose_name="Quantidade Recebida"
    )
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
    data_validade = models.DateField(null=True, blank=True, verbose_name="Data de Validade")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Item da Ordem de Compra"
        verbose_name_plural = "Itens das Ordens de Compra"
        ordering = ['ordem_compra', 'insumo']
    
    def __str__(self):
        return f"{self.ordem_compra.numero_ordem} - {self.insumo.nome}"


class MovimentacaoEstoque(models.Model):
    """Movimentações de estoque de insumos"""
    TIPO_CHOICES = [
        ('ENTRADA_COMPRA', 'Entrada - Compra'),
        ('ENTRADA_AJUSTE', 'Entrada - Ajuste de Inventário'),
        ('ENTRADA_TRANSFERENCIA', 'Entrada - Transferência'),
        ('SAIDA_CONSUMO', 'Saída - Consumo'),
        ('SAIDA_VENDA', 'Saída - Venda'),
        ('SAIDA_PERDA', 'Saída - Perda/Desperdício'),
        ('SAIDA_TRANSFERENCIA', 'Saída - Transferência'),
        ('AJUSTE_INVENTARIO', 'Ajuste - Inventário'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='movimentacoes_estoque',
        verbose_name="Propriedade"
    )
    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        related_name='movimentacoes',
        verbose_name="Insumo"
    )
    tipo_movimentacao = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Movimentação"
    )
    quantidade = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="Quantidade"
    )
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
    data_movimentacao = models.DateField(verbose_name="Data da Movimentação")
    ordem_compra = models.ForeignKey(
        OrdemCompra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes',
        verbose_name="Ordem de Compra"
    )
    lote_confinamento = models.ForeignKey(
        'LoteConfinamento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_insumos',
        verbose_name="Lote de Confinamento"
    )
    propriedade_destino = models.ForeignKey(
        Propriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_recebidas',
        verbose_name="Propriedade Destino (para transferências)"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Usuário"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-data_movimentacao', '-data_registro']
        indexes = [
            models.Index(fields=['propriedade', 'insumo', 'data_movimentacao']),
            models.Index(fields=['tipo_movimentacao', 'data_movimentacao']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_movimentacao_display()} - {self.insumo.nome} - {self.data_movimentacao}"


