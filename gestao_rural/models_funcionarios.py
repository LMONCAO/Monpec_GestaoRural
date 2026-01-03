# -*- coding: utf-8 -*-
"""
Modelos para Gestão de Funcionários Rurais
- Cadastro de funcionários
- Controle de salários
- Descontos e impostos
- Geração de holerite
- Controle de ponto
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .models import Propriedade


# ============================================================================
# CADASTRO DE FUNCIONÁRIOS
# ============================================================================

class Funcionario(models.Model):
    """Cadastro de funcionários"""
    TIPO_CONTRATO_CHOICES = [
        ('CLT', 'CLT'),
        ('TEMPORARIO', 'Temporário'),
        ('AUTONOMO', 'Autônomo'),
        ('TERCEIRIZADO', 'Terceirizado'),
        ('ESTAGIARIO', 'Estagiário'),
    ]
    
    SITUACAO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('AFASTADO', 'Afastado'),
        ('FERIAS', 'Férias'),
        ('LICENCA', 'Licença Médica'),
        ('DEMITIDO', 'Demitido'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='funcionarios',
        verbose_name="Propriedade"
    )
    
    # Dados Pessoais
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG")
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    sexo = models.CharField(
        max_length=1,
        choices=[('M', 'Masculino'), ('F', 'Feminino')],
        blank=True,
        null=True,
        verbose_name="Sexo"
    )
    
    # Contato
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    celular = models.CharField(max_length=20, blank=True, null=True, verbose_name="Celular")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    
    # Dados Trabalhistas
    tipo_contrato = models.CharField(
        max_length=20,
        choices=TIPO_CONTRATO_CHOICES,
        default='CLT',
        verbose_name="Tipo de Contrato"
    )
    cargo = models.CharField(max_length=100, verbose_name="Cargo/Função")
    data_admissao = models.DateField(verbose_name="Data de Admissão")
    data_demissao = models.DateField(null=True, blank=True, verbose_name="Data de Demissão")
    situacao = models.CharField(
        max_length=20,
        choices=SITUACAO_CHOICES,
        default='ATIVO',
        verbose_name="Situação"
    )
    
    # Salário
    salario_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Salário Base (R$)"
    )
    jornada_trabalho = models.IntegerField(
        default=44,
        verbose_name="Jornada de Trabalho (horas/semana)"
    )
    
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
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"
        ordering = ['nome', 'propriedade']
    
    def __str__(self):
        return f"{self.nome} - {self.cargo} - {self.propriedade.nome_propriedade}"
    
    @property
    def ativo(self):
        return self.situacao == 'ATIVO'


# ============================================================================
# CONTROLE DE PONTO
# ============================================================================

class PontoFuncionario(models.Model):
    """Controle de ponto dos funcionários"""
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='pontos',
        verbose_name="Funcionário"
    )
    data = models.DateField(verbose_name="Data")
    
    # Horários
    entrada_manha = models.TimeField(null=True, blank=True, verbose_name="Entrada Manhã")
    saida_manha = models.TimeField(null=True, blank=True, verbose_name="Saída Manhã")
    entrada_tarde = models.TimeField(null=True, blank=True, verbose_name="Entrada Tarde")
    saida_tarde = models.TimeField(null=True, blank=True, verbose_name="Saída Tarde")
    
    # Cálculos
    horas_trabalhadas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Horas Trabalhadas"
    )
    horas_extras = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Horas Extras"
    )
    horas_faltas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Horas Faltas"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Ponto"
        verbose_name_plural = "Pontos"
        ordering = ['-data', 'funcionario']
        unique_together = ['funcionario', 'data']
    
    def __str__(self):
        return f"{self.funcionario.nome} - {self.data}"


# ============================================================================
# FOLHA DE PAGAMENTO
# ============================================================================

class FolhaPagamento(models.Model):
    """Folha de pagamento mensal"""
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('FECHADA', 'Fechada'),
        ('PAGA', 'Paga'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='folhas_pagamento',
        verbose_name="Propriedade"
    )
    competencia = models.CharField(
        max_length=7,
        verbose_name="Competência",
        help_text="Formato: MM/AAAA"
    )
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ABERTA',
        verbose_name="Status"
    )
    
    # Totais
    total_proventos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Total de Proventos (R$)"
    )
    total_descontos = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Total de Descontos (R$)"
    )
    total_liquido = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Total Líquido (R$)"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_fechamento = models.DateTimeField(null=True, blank=True, verbose_name="Data de Fechamento")
    
    class Meta:
        verbose_name = "Folha de Pagamento"
        verbose_name_plural = "Folhas de Pagamento"
        ordering = ['-competencia', 'propriedade']
        unique_together = ['propriedade', 'competencia']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.competencia}"


# ============================================================================
# HOLERITE / CONTRACHEQUE
# ============================================================================

class Holerite(models.Model):
    """Holerite individual do funcionário"""
    folha_pagamento = models.ForeignKey(
        FolhaPagamento,
        on_delete=models.CASCADE,
        related_name='holerites',
        verbose_name="Folha de Pagamento"
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='holerites',
        verbose_name="Funcionário"
    )
    
    # PROVENTOS
    salario_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Salário Base"
    )
    horas_extras = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Horas Extras"
    )
    valor_horas_extras = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Horas Extras (R$)"
    )
    adicional_noturno = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Adicional Noturno (R$)"
    )
    comissao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Comissão (R$)"
    )
    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Bônus (R$)"
    )
    dias_trabalhados = models.IntegerField(
        default=0,
        verbose_name="Dias Trabalhados"
    )
    dias_faltas = models.IntegerField(
        default=0,
        verbose_name="Dias Faltas"
    )
    
    # DESCONTOS
    # INSS
    desconto_inss = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Desconto INSS (R$)"
    )
    base_calculo_inss = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Base de Cálculo INSS (R$)"
    )
    
    # IRRF
    desconto_irrf = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Desconto IRRF (R$)"
    )
    base_calculo_irrf = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Base de Cálculo IRRF (R$)"
    )
    numero_dependentes = models.IntegerField(
        default=0,
        verbose_name="Número de Dependentes"
    )
    
    # FGTS
    base_calculo_fgts = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Base de Cálculo FGTS (R$)"
    )
    valor_fgts = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor FGTS (R$)"
    )
    
    # Outros Descontos
    desconto_vale_transporte = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Vale Transporte (R$)"
    )
    desconto_vale_refeicao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Vale Refeição (R$)"
    )
    desconto_plano_saude = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Plano de Saúde (R$)"
    )
    desconto_emprestimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Empréstimo (R$)"
    )
    desconto_outros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Outros Descontos (R$)"
    )
    
    # TOTAIS
    total_proventos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Total de Proventos (R$)"
    )
    total_descontos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Total de Descontos (R$)"
    )
    valor_liquido = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Valor Líquido a Receber (R$)"
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Holerite"
        verbose_name_plural = "Holerites"
        ordering = ['-folha_pagamento__competencia', 'funcionario']
        unique_together = ['folha_pagamento', 'funcionario']
    
    def __str__(self):
        return f"{self.funcionario.nome} - {self.folha_pagamento.competencia}"


# ============================================================================
# DESCONTOS PERSONALIZADOS
# ============================================================================

class DescontoFuncionario(models.Model):
    """Descontos personalizados para funcionários"""
    TIPO_CHOICES = [
        ('VALE_TRANSPORTE', 'Vale Transporte'),
        ('VALE_REFEICAO', 'Vale Refeição'),
        ('PLANO_SAUDE', 'Plano de Saúde'),
        ('EMPRESTIMO', 'Empréstimo'),
        ('ADVOGADO', 'Advogado'),
        ('OUTROS', 'Outros'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('SUSPENSO', 'Suspenso'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='descontos',
        verbose_name="Funcionário"
    )
    tipo_desconto = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Desconto"
    )
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor (R$)"
    )
    percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Percentual (%)",
        help_text="Se preenchido, calcula sobre o salário"
    )
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Término",
        help_text="Deixe vazio para desconto permanente"
    )
    numero_parcelas = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Parcelas",
        help_text="Para descontos parcelados"
    )
    parcelas_pagas = models.IntegerField(
        default=0,
        verbose_name="Parcelas Pagas"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ATIVO',
        verbose_name="Status"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Desconto de Funcionário"
        verbose_name_plural = "Descontos de Funcionários"
        ordering = ['funcionario', 'data_inicio']
    
    def __str__(self):
        return f"{self.funcionario.nome} - {self.get_tipo_desconto_display()} - R$ {self.valor}"


# ============================================================================
# UTILITÁRIOS DE CÁLCULO
# ============================================================================

class CalculadoraImpostos:
    """Calculadora de impostos trabalhistas"""
    
    # Tabelas INSS 2024
    TABELA_INSS = [
        (0, 1412.00, 0.075),
        (1412.01, 2666.68, 0.09),
        (2666.69, 4000.03, 0.12),
        (4000.04, 7786.02, 0.14),
    ]
    
    # Tabela IRRF 2024
    TABELA_IRRF = [
        (0, 2282.00, 0, 0),
        (2282.01, 3391.00, 0.075, 171.82),
        (3391.01, 4502.00, 0.15, 257.82),
        (4502.01, 5597.00, 0.225, 413.82),
        (5597.01, float('inf'), 0.275, 701.82),
    ]
    
    @staticmethod
    def calcular_inss(salario_base):
        """Calcula desconto INSS"""
        if salario_base <= 0:
            return Decimal('0.00')
        
        if salario_base > 7786.02:
            # Teto do INSS
            base = Decimal('7786.02')
        else:
            base = Decimal(str(salario_base))
        
        for faixa_min, faixa_max, aliquota in CalculadoraImpostos.TABELA_INSS:
            if base >= Decimal(str(faixa_min)) and base <= Decimal(str(faixa_max)):
                desconto = base * Decimal(str(aliquota))
                return desconto.quantize(Decimal('0.01'))
        
        return Decimal('0.00')
    
    @staticmethod
    def calcular_irrf(salario_base, dependentes=0):
        """Calcula desconto IRRF"""
        if salario_base <= 0:
            return Decimal('0.00')
        
        # Dedução por dependente (2024)
        deducao_dependente = Decimal('189.59')
        deducao_total = deducao_dependente * Decimal(str(dependentes))
        
        base_calculo = Decimal(str(salario_base)) - deducao_total
        
        if base_calculo <= 0:
            return Decimal('0.00')
        
        for faixa_min, faixa_max, aliquota, deducao in CalculadoraImpostos.TABELA_IRRF:
            if base_calculo >= Decimal(str(faixa_min)) and base_calculo <= Decimal(str(faixa_max)):
                imposto = (base_calculo * Decimal(str(aliquota))) - Decimal(str(deducao))
                return max(Decimal('0.00'), imposto.quantize(Decimal('0.01')))
        
        return Decimal('0.00')
    
    @staticmethod
    def calcular_fgts(salario_base):
        """Calcula FGTS (8% sobre salário)"""
        if salario_base <= 0:
            return Decimal('0.00')
        
        return (Decimal(str(salario_base)) * Decimal('0.08')).quantize(Decimal('0.01'))


