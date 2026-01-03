# -*- coding: utf-8 -*-
"""
Modelos para Controle Reprodutivo Pecuário
- IATF (Inseminação Artificial em Tempo Fixo)
- Monta Natural
- Controle de Touros
- Calendário Reprodutivo
- Estação de Monta
- Nascimentos
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from .models import Propriedade, CategoriaAnimal, AnimalIndividual


# ============================================================================
# CONTROLE DE TOUROS
# ============================================================================

class Touro(models.Model):
    """Cadastro de touros reprodutores"""
    STATUS_CHOICES = [
        ('APTO', 'Apto para Reprodução'),
        ('INAPTO', 'Inapto para Reprodução'),
        ('EM_TRATAMENTO', 'Em Tratamento'),
        ('AFASTADO', 'Afastado'),
        ('VENDIDO', 'Vendido'),
        ('MORTO', 'Morto'),
    ]
    
    PROPRIEDADE_CHOICES = [
        ('PROPRIO', 'Próprio'),
        ('REPRODUTOR', 'Reprodutor Alugado'),
        ('TERCEIROS', 'Touro de Terceiros'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='touros',
        verbose_name="Propriedade"
    )
    animal_individual = models.OneToOneField(
        AnimalIndividual,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='touro',
        verbose_name="Animal Individual"
    )
    
    # Identificação
    numero_brinco = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número do Brinco"
    )
    nome = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nome do Touro"
    )
    raca = models.CharField(
        max_length=50,
        verbose_name="Raça"
    )
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Nascimento"
    )
    
    # Status Reprodutivo
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='APTO',
        verbose_name="Status"
    )
    propriedade_touro = models.CharField(
        max_length=20,
        choices=PROPRIEDADE_CHOICES,
        default='PROPRIO',
        verbose_name="Propriedade do Touro"
    )
    
    # Dados Reprodutivos
    data_primeiro_servico = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do Primeiro Serviço"
    )
    numero_servicos = models.IntegerField(
        default=0,
        verbose_name="Número de Serviços Realizados"
    )
    numero_prenhezes = models.IntegerField(
        default=0,
        verbose_name="Número de Prenhezes"
    )
    taxa_prenhez = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Taxa de Prenhez (%)",
        help_text="Calculado automaticamente"
    )
    
    # Avaliação Andrológica
    data_ultima_avaliacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Última Avaliação Andrológica"
    )
    resultado_avaliacao = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Resultado da Avaliação",
        help_text="Apto, Inapto, Condicional"
    )
    observacoes_avaliacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações da Avaliação"
    )
    
    # Valores
    valor_aquisicao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor de Aquisição (R$)"
    )
    valor_aluguel_mensal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor de Aluguel Mensal (R$)"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Touro Reprodutor"
        verbose_name_plural = "Touros Reprodutores"
        ordering = ['numero_brinco', 'nome']
    
    def __str__(self):
        return f"{self.numero_brinco} - {self.nome or 'Sem Nome'}"
    
    def calcular_taxa_prenhez(self):
        """Calcula taxa de prenhez"""
        if self.numero_servicos > 0:
            taxa = (Decimal(str(self.numero_prenhezes)) / Decimal(str(self.numero_servicos))) * 100
            self.taxa_prenhez = taxa
            return taxa
        return Decimal('0.00')
    
    def save(self, *args, **kwargs):
        self.calcular_taxa_prenhez()
        super().save(*args, **kwargs)


# ============================================================================
# ESTAÇÃO DE MONTA
# ============================================================================

class EstacaoMonta(models.Model):
    """Estação de monta da propriedade"""
    TIPO_CHOICES = [
        ('FIXA', 'Estação de Monta Fixa'),
        ('CONTINUA', 'Monta Contínua'),
        ('IATF', 'IATF Programada'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='estacoes_monta',
        verbose_name="Propriedade"
    )
    nome = models.CharField(
        max_length=200,
        verbose_name="Nome da Estação de Monta"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='FIXA',
        verbose_name="Tipo"
    )
    
    # Período
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Término")
    dias_duracao = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Duração (dias)",
        help_text="Calculado automaticamente"
    )
    
    # Objetivos
    numero_vacas_objetivo = models.IntegerField(
        default=0,
        verbose_name="Número de Vacas (Objetivo)"
    )
    taxa_prenhez_objetivo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=85.00,
        verbose_name="Taxa de Prenhez Objetivo (%)"
    )
    
    # Resultados
    numero_vacas_inseminadas = models.IntegerField(
        default=0,
        verbose_name="Número de Vacas Inseminadas"
    )
    numero_vacas_monta_natural = models.IntegerField(
        default=0,
        verbose_name="Número de Vacas em Monta Natural"
    )
    numero_prenhezes = models.IntegerField(
        default=0,
        verbose_name="Número de Prenhezes"
    )
    taxa_prenhez_real = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Taxa de Prenhez Real (%)",
        help_text="Calculado automaticamente"
    )
    
    # Status
    ativa = models.BooleanField(
        default=True,
        verbose_name="Estação Ativa"
    )
    finalizada = models.BooleanField(
        default=False,
        verbose_name="Finalizada"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Estação de Monta"
        verbose_name_plural = "Estações de Monta"
        ordering = ['-data_inicio', 'propriedade']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.nome} ({self.data_inicio} a {self.data_fim})"
    
    def calcular_duracao(self):
        """Calcula duração em dias"""
        if self.data_inicio and self.data_fim:
            delta = self.data_fim - self.data_inicio
            self.dias_duracao = delta.days
            return delta.days
        return 0
    
    def calcular_taxa_prenhez_real(self):
        """Calcula taxa de prenhez real"""
        total_vacas = self.numero_vacas_inseminadas + self.numero_vacas_monta_natural
        if total_vacas > 0 and self.numero_prenhezes > 0:
            taxa = (Decimal(str(self.numero_prenhezes)) / Decimal(str(total_vacas))) * 100
            self.taxa_prenhez_real = taxa
            return taxa
        return Decimal('0.00')
    
    def save(self, *args, **kwargs):
        self.calcular_duracao()
        self.calcular_taxa_prenhez_real()
        super().save(*args, **kwargs)


# ============================================================================
# IATF - INSEMINAÇÃO ARTIFICIAL EM TEMPO FIXO
# ============================================================================

class IATF(models.Model):
    """Inseminação Artificial em Tempo Fixo"""
    STATUS_CHOICES = [
        ('PROGRAMADA', 'Programada'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
        ('FALHOU', 'Falhou'),
    ]
    
    RESULTADO_CHOICES = [
        ('PENDENTE', 'Pendente Diagnóstico'),
        ('PREMIDA', 'Prenhez Confirmada'),
        ('VAZIA', 'Vazia'),
        ('ABORTO', 'Aborto'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='iatfs',
        verbose_name="Propriedade"
    )
    estacao_monta = models.ForeignKey(
        EstacaoMonta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs',
        verbose_name="Estação de Monta"
    )
    animal_individual = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='iatfs',
        verbose_name="Animal"
    )
    
    # Data e Protocolo
    data_programada = models.DateField(verbose_name="Data Programada")
    data_realizacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Realização"
    )
    protocolo = models.CharField(
        max_length=100,
        verbose_name="Protocolo IATF",
        help_text="Ex: Ovsynch, CIDR, etc."
    )
    
    # Sêmen
    raca_semen = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Raça do Sêmen"
    )
    numero_touro = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número do Touro (Sêmen)"
    )
    lote_semen = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Lote do Sêmen"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PROGRAMADA',
        verbose_name="Status"
    )
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        default='PENDENTE',
        verbose_name="Resultado"
    )
    
    # Diagnóstico de Prenhez
    data_diagnostico = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do Diagnóstico"
    )
    dias_gestacao_diagnostico = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dias de Gestação no Diagnóstico"
    )
    
    # Custos
    custo_semen = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Custo do Sêmen (R$)"
    )
    custo_inseminacao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Custo da Inseminação (R$)"
    )
    custo_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Custo Total (R$)"
    )
    
    # Responsáveis
    inseminador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs_inseminadas',
        verbose_name="Inseminador"
    )
    veterinario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs_veterinario_simples',
        verbose_name="Veterinário"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "IATF"
        verbose_name_plural = "IATFs"
        ordering = ['-data_programada', 'animal_individual']
    
    def __str__(self):
        return f"{self.animal_individual.numero_brinco} - {self.data_programada} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Calcular custo total
        custo_total = Decimal('0.00')
        if self.custo_semen:
            custo_total += self.custo_semen
        if self.custo_inseminacao:
            custo_total += self.custo_inseminacao
        self.custo_total = custo_total if custo_total > 0 else None
        
        super().save(*args, **kwargs)


# ============================================================================
# MONTA NATURAL
# ============================================================================

class MontaNatural(models.Model):
    """Controle de monta natural"""
    STATUS_CHOICES = [
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    RESULTADO_CHOICES = [
        ('PENDENTE', 'Pendente Diagnóstico'),
        ('PREMIDA', 'Prenhez Confirmada'),
        ('VAZIA', 'Vazia'),
        ('ABORTO', 'Aborto'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='montas_naturais',
        verbose_name="Propriedade"
    )
    estacao_monta = models.ForeignKey(
        EstacaoMonta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='montas_naturais',
        verbose_name="Estação de Monta"
    )
    touro = models.ForeignKey(
        Touro,
        on_delete=models.CASCADE,
        related_name='montas_naturais',
        verbose_name="Touro"
    )
    animal_individual = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='montas_naturais',
        verbose_name="Vaca"
    )
    
    # Data
    data_cobertura = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Cobertura Observada"
    )
    data_estimada_cobertura = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data Estimada de Cobertura",
        help_text="Baseado no cio observado"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EM_ANDAMENTO',
        verbose_name="Status"
    )
    resultado = models.CharField(
        max_length=20,
        choices=RESULTADO_CHOICES,
        default='PENDENTE',
        verbose_name="Resultado"
    )
    
    # Diagnóstico de Prenhez
    data_diagnostico = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do Diagnóstico"
    )
    dias_gestacao_diagnostico = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dias de Gestação no Diagnóstico"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Monta Natural"
        verbose_name_plural = "Montas Naturais"
        ordering = ['-data_estimada_cobertura', 'animal_individual']
    
    def __str__(self):
        return f"{self.animal_individual.numero_brinco} - Touro {self.touro.numero_brinco} - {self.get_status_display()}"


# ============================================================================
# NASCIMENTOS
# ============================================================================

class Nascimento(models.Model):
    """Controle de nascimentos"""
    TIPO_CHOICES = [
        ('NORMAL', 'Nascimento Normal'),
        ('CESAREA', 'Cesariana'),
        ('DIFICIL', 'Parto Difícil'),
        ('NATIMORTO', 'Natimorto'),
    ]
    
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('F', 'Fêmea'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='nascimentos',
        verbose_name="Propriedade"
    )
    
    # Mãe
    mae = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='nascimentos_mae',
        verbose_name="Mãe"
    )
    
    # Origem da gestação
    iatf = models.ForeignKey(
        IATF,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nascimentos',
        verbose_name="IATF de Origem"
    )
    monta_natural = models.ForeignKey(
        MontaNatural,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nascimentos',
        verbose_name="Monta Natural de Origem"
    )
    
    # Dados do nascimento
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    hora_nascimento = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora do Nascimento"
    )
    tipo_parto = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='NORMAL',
        verbose_name="Tipo de Parto"
    )
    
    # Bezerro
    numero_brinco_bezerro = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número do Brinco do Bezerro"
    )
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        verbose_name="Sexo"
    )
    peso_nascimento = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso ao Nascimento (kg)"
    )
    
    # Animais
    animal_individual = models.OneToOneField(
        AnimalIndividual,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nascimento',
        verbose_name="Animal Individual Criado"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável pelo Registro"
    )
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Nascimento"
        verbose_name_plural = "Nascimentos"
        ordering = ['-data_nascimento', 'mae']
    
    def __str__(self):
        return f"{self.mae.numero_brinco} - {self.data_nascimento} - {self.get_sexo_display()}"


# ============================================================================
# CALENDÁRIO REPRODUTIVO
# ============================================================================

class CalendarioReprodutivo(models.Model):
    """Calendário reprodutivo da propriedade"""
    TIPO_EVENTO_CHOICES = [
        ('ESTACAO_MONTA', 'Estação de Monta'),
        ('IATF', 'IATF'),
        ('DIAGNOSTICO', 'Diagnóstico de Prenhez'),
        ('SECAGEM', 'Secagem de Vacas'),
        ('PRE_PARTO', 'Pré-Parto'),
        ('PARTO', 'Parto Previsto'),
        ('AVALIACAO_TOURO', 'Avaliação Andrológica de Touros'),
        ('OUTROS', 'Outros'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='calendario_reprodutivo',
        verbose_name="Propriedade"
    )
    tipo_evento = models.CharField(
        max_length=30,
        choices=TIPO_EVENTO_CHOICES,
        verbose_name="Tipo de Evento"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    # Datas
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Término"
    )
    
    # Relacionamentos
    estacao_monta = models.ForeignKey(
        EstacaoMonta,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='eventos_calendario',
        verbose_name="Estação de Monta"
    )
    
    # Status
    concluido = models.BooleanField(
        default=False,
        verbose_name="Concluído"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Evento do Calendário Reprodutivo"
        verbose_name_plural = "Calendário Reprodutivo"
        ordering = ['data_inicio', 'tipo_evento']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.titulo} - {self.data_inicio}"

