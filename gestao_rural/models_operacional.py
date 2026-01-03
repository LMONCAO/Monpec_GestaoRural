# -*- coding: utf-8 -*-
"""
Modelos Operacionais - Controles de Despesas Principais
- Combustível (Óleo Diesel)
- Suplementação (com estoque)
- Funcionários (já criado em models_funcionarios.py)
- Empreiteiros
- Manutenção de Equipamentos
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from .models import Propriedade


# ============================================================================
# CONTROLE DE COMBUSTÍVEL (ÓLEO DIESEL)
# ============================================================================

class TanqueCombustivel(models.Model):
    """Cadastro de tanques de combustível"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='tanques_combustivel',
        verbose_name="Propriedade"
    )
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome/Identificação do Tanque"
    )
    capacidade_litros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Capacidade (litros)"
    )
    estoque_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Estoque Atual (litros)"
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Estoque Mínimo (litros)",
        help_text="Alerta quando atingir"
    )
    localizacao = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Localização"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Tanque de Combustível"
        verbose_name_plural = "Tanques de Combustível"
        ordering = ['propriedade', 'nome']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.nome}"


class AbastecimentoCombustivel(models.Model):
    """Controle de abastecimento de combustível"""
    TIPO_CHOICES = [
        ('COMPRA', 'Compra'),
        ('TRANSFERENCIA', 'Transferência'),
        ('AJUSTE', 'Ajuste de Estoque'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='abastecimentos',
        verbose_name="Propriedade"
    )
    tanque = models.ForeignKey(
        TanqueCombustivel,
        on_delete=models.CASCADE,
        related_name='abastecimentos',
        verbose_name="Tanque"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='COMPRA',
        verbose_name="Tipo"
    )
    
    # Dados da Compra/Abastecimento
    data = models.DateField(verbose_name="Data")
    fornecedor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Fornecedor"
    )
    numero_nota_fiscal = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número da Nota Fiscal"
    )
    
    # Quantidades
    quantidade_litros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade (litros)"
    )
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Unitário (R$/litro)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Abastecimento de Combustível"
        verbose_name_plural = "Abastecimentos de Combustível"
        ordering = ['-data', 'tanque']
    
    def __str__(self):
        return f"{self.tanque.nome} - {self.quantidade_litros}L - {self.data}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        if self.quantidade_litros and self.preco_unitario:
            self.valor_total = self.quantidade_litros * self.preco_unitario
        
        super().save(*args, **kwargs)
        
        # Atualizar estoque do tanque
        if self.tipo == 'COMPRA':
            self.tanque.estoque_atual += self.quantidade_litros
            self.tanque.save()


class ConsumoCombustivel(models.Model):
    """Controle de consumo de combustível"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='consumos_combustivel',
        verbose_name="Propriedade"
    )
    tanque = models.ForeignKey(
        TanqueCombustivel,
        on_delete=models.CASCADE,
        related_name='consumos',
        verbose_name="Tanque"
    )
    data = models.DateField(verbose_name="Data")
    
    # Equipamento/Veículo
    tipo_equipamento = models.CharField(
        max_length=100,
        verbose_name="Tipo de Equipamento",
        help_text="Trator, Caminhão, Máquina, etc."
    )
    identificacao = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Identificação",
        help_text="Número do equipamento, placa, etc."
    )
    
    # Consumo
    quantidade_litros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade Consumida (litros)"
    )
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Unitário (R$/litro)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )
    
    # Finalidade
    finalidade = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Finalidade",
        help_text="Ex: Plantio, Colheita, Transporte, etc."
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Consumo de Combustível"
        verbose_name_plural = "Consumos de Combustível"
        ordering = ['-data', 'tanque']
    
    def __str__(self):
        return f"{self.tanque.nome} - {self.quantidade_litros}L - {self.data}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        if self.quantidade_litros and self.valor_unitario:
            self.valor_total = self.quantidade_litros * self.valor_unitario
        
        super().save(*args, **kwargs)
        
        # Atualizar estoque do tanque
        if self.tanque.estoque_atual >= self.quantidade_litros:
            self.tanque.estoque_atual -= self.quantidade_litros
            self.tanque.save()


# ============================================================================
# CONTROLE DE SUPLEMENTAÇÃO (COM ESTOQUE)
# ============================================================================

class EstoqueSuplementacao(models.Model):
    """Estoque de suplementação (sal, ração, etc.)"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='estoques_suplementacao',
        verbose_name="Propriedade"
    )
    tipo_suplemento = models.CharField(
        max_length=100,
        verbose_name="Tipo de Suplemento",
        help_text="Sal mineral, Ração, Suplemento proteico, etc."
    )
    unidade_medida = models.CharField(
        max_length=20,
        default='KG',
        verbose_name="Unidade de Medida"
    )
    
    # Estoque
    quantidade_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Quantidade Atual"
    )
    quantidade_minima = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Quantidade Mínima",
        help_text="Alerta quando atingir"
    )
    
    # Valores
    valor_unitario_medio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Unitário Médio (R$)"
    )
    valor_total_estoque = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Valor Total do Estoque (R$)"
    )
    
    localizacao = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Localização"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Estoque de Suplementação"
        verbose_name_plural = "Estoques de Suplementação"
        ordering = ['propriedade', 'tipo_suplemento']
        unique_together = ['propriedade', 'tipo_suplemento']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.tipo_suplemento} - {self.quantidade_atual} {self.unidade_medida}"


class CompraSuplementacao(models.Model):
    """Compras de suplementação"""
    estoque = models.ForeignKey(
        EstoqueSuplementacao,
        on_delete=models.CASCADE,
        related_name='compras',
        verbose_name="Estoque"
    )
    data = models.DateField(verbose_name="Data da Compra")
    fornecedor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Fornecedor"
    )
    numero_nota_fiscal = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número da Nota Fiscal"
    )
    
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade"
    )
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Unitário (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Compra de Suplementação"
        verbose_name_plural = "Compras de Suplementação"
        ordering = ['-data', 'estoque']
    
    def __str__(self):
        return f"{self.estoque.tipo_suplemento} - {self.quantidade} - {self.data}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        if self.quantidade and self.preco_unitario:
            self.valor_total = self.quantidade * self.preco_unitario
        
        super().save(*args, **kwargs)
        
        # Atualizar estoque
        self.estoque.quantidade_atual += self.quantidade
        
        # Atualizar preço médio
        if self.estoque.quantidade_atual > 0:
            valor_total_antigo = self.estoque.valor_total_estoque
            valor_total_novo = valor_total_antigo + self.valor_total
            self.estoque.valor_unitario_medio = valor_total_novo / self.estoque.quantidade_atual
        
        self.estoque.valor_total_estoque += self.valor_total
        self.estoque.save()


class DistribuicaoSuplementacao(models.Model):
    """Distribuição de suplementação no pasto"""
    estoque = models.ForeignKey(
        EstoqueSuplementacao,
        on_delete=models.CASCADE,
        related_name='distribuicoes',
        verbose_name="Estoque"
    )
    data = models.DateField(verbose_name="Data da Distribuição")
    pastagem = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Pastagem/Piquete"
    )
    
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade Distribuída"
    )
    numero_animais = models.IntegerField(
        default=0,
        verbose_name="Número de Animais"
    )
    quantidade_por_animal = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Quantidade por Animal",
        help_text="Calculado automaticamente"
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
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Distribuição de Suplementação"
        verbose_name_plural = "Distribuições de Suplementação"
        ordering = ['-data', 'estoque']
    
    def __str__(self):
        return f"{self.estoque.tipo_suplemento} - {self.quantidade} - {self.data}"
    
    def save(self, *args, **kwargs):
        # Calcular quantidade por animal
        if self.numero_animais > 0 and self.quantidade:
            self.quantidade_por_animal = self.quantidade / Decimal(str(self.numero_animais))
        
        # Calcular valor total
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
        
        super().save(*args, **kwargs)
        
        # Atualizar estoque
        if self.estoque.quantidade_atual >= self.quantidade:
            self.estoque.quantidade_atual -= self.quantidade
            self.estoque.valor_total_estoque -= self.valor_total
            self.estoque.save()


# ============================================================================
# CONTROLE DE EMPREITEIROS
# ============================================================================

class Empreiteiro(models.Model):
    """Cadastro de empreiteiros"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='empreiteiros',
        verbose_name="Propriedade"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome/Razão Social")
    cpf_cnpj = models.CharField(
        max_length=18,
        verbose_name="CPF/CNPJ"
    )
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    
    # Especialidade
    especialidade = models.CharField(
        max_length=200,
        verbose_name="Especialidade",
        help_text="Ex: Construção, Reforma, Manutenção, etc."
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Empreiteiro"
        verbose_name_plural = "Empreiteiros"
        ordering = ['nome', 'propriedade']
    
    def __str__(self):
        return f"{self.nome} - {self.especialidade}"


class ServicoEmpreiteiro(models.Model):
    """Serviços prestados por empreiteiros"""
    STATUS_CHOICES = [
        ('ORCAMENTO', 'Orçamento'),
        ('APROVADO', 'Aprovado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='servicos_empreiteiros',
        verbose_name="Propriedade"
    )
    empreiteiro = models.ForeignKey(
        Empreiteiro,
        on_delete=models.CASCADE,
        related_name='servicos',
        verbose_name="Empreiteiro"
    )
    
    # Dados do Serviço
    descricao = models.CharField(max_length=200, verbose_name="Descrição do Serviço")
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Término")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ORCAMENTO',
        verbose_name="Status"
    )
    
    # Valores
    valor_orcamento = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor do Orçamento (R$)"
    )
    valor_final = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Final (R$)"
    )
    
    # Pagamento
    forma_pagamento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Forma de Pagamento"
    )
    data_pagamento = models.DateField(null=True, blank=True, verbose_name="Data de Pagamento")
    pago = models.BooleanField(default=False, verbose_name="Pago")
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Serviço de Empreiteiro"
        verbose_name_plural = "Serviços de Empreiteiros"
        ordering = ['-data_inicio', 'empreiteiro']
    
    def __str__(self):
        return f"{self.empreiteiro.nome} - {self.descricao} - {self.get_status_display()}"


# ============================================================================
# CONTROLE DE MANUTENÇÃO
# ============================================================================

class TipoEquipamento(models.Model):
    """Tipos de equipamentos"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Tipo de Equipamento"
        verbose_name_plural = "Tipos de Equipamentos"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Equipamento(models.Model):
    """Cadastro de equipamentos"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='equipamentos',
        verbose_name="Propriedade"
    )
    tipo = models.ForeignKey(
        TipoEquipamento,
        on_delete=models.CASCADE,
        verbose_name="Tipo"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome/Identificação")
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Série")
    ano = models.IntegerField(null=True, blank=True, verbose_name="Ano")
    
    # Valores
    valor_aquisicao = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor de Aquisição (R$)"
    )
    data_aquisicao = models.DateField(null=True, blank=True, verbose_name="Data de Aquisição")
    
    # Manutenção
    horas_ultima_revisao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Horas na Última Revisão"
    )
    horas_entre_revisoes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100,
        verbose_name="Horas entre Revisões"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"
        ordering = ['propriedade', 'tipo', 'nome']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.nome}"


class ManutencaoEquipamento(models.Model):
    """Manutenções de equipamentos"""
    TIPO_CHOICES = [
        ('PREVENTIVA', 'Preventiva'),
        ('CORRETIVA', 'Corretiva'),
        ('REVISAO', 'Revisão'),
        ('CONSERTO', 'Conserto'),
    ]
    
    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='manutencoes',
        verbose_name="Propriedade"
    )
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.CASCADE,
        related_name='manutencoes',
        verbose_name="Equipamento"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Manutenção"
    )
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    
    # Datas
    data_agendamento = models.DateField(verbose_name="Data Agendada")
    data_realizacao = models.DateField(null=True, blank=True, verbose_name="Data de Realização")
    
    # Valores
    valor_pecas = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor de Peças (R$)"
    )
    valor_mao_obra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor de Mão de Obra (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Valor Total (R$)"
    )
    
    # Fornecedor/Serviço
    fornecedor_servico = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Fornecedor/Serviço"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AGENDADA',
        verbose_name="Status"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Manutenção de Equipamento"
        verbose_name_plural = "Manutenções de Equipamentos"
        ordering = ['-data_agendamento', 'equipamento']
    
    def __str__(self):
        return f"{self.equipamento.nome} - {self.get_tipo_display()} - {self.data_agendamento}"
    
    def save(self, *args, **kwargs):
        # Calcular valor total
        self.valor_total = self.valor_pecas + self.valor_mao_obra
        super().save(*args, **kwargs)
