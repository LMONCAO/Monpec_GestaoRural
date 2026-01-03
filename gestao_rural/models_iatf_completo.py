# -*- coding: utf-8 -*-
"""
Modelos Completos para IATF (Inseminação Artificial em Tempo Fixo)
Sistema profissional e completo de gestão de IATF
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date, timedelta
from .models import Propriedade, CategoriaAnimal, AnimalIndividual


# ============================================================================
# PROTOCOLOS IATF
# ============================================================================

class ProtocoloIATF(models.Model):
    """Protocolos de IATF (Ovsynch, CIDR, etc.)"""
    TIPO_PROTOCOLO_CHOICES = [
        ('OVSYNCH', 'Ovsynch'),
        ('OVSYNCH_7', 'Ovsynch 7 dias'),
        ('CIDR', 'CIDR'),
        ('CIDR_Ovsynch', 'CIDR + Ovsynch'),
        ('DUPLO_Ovsynch', 'Duplo Ovsynch'),
        ('J_Synch', 'J-Synch'),
        ('PROESTRO', 'Proestro'),
        ('CUSTOMIZADO', 'Customizado'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome do Protocolo")
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_PROTOCOLO_CHOICES,
        verbose_name="Tipo de Protocolo"
    )
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    # Dias do protocolo
    dia_gnrh = models.IntegerField(
        default=0,
        verbose_name="Dia 0 - GnRH",
        help_text="Dia inicial (dia 0)"
    )
    dia_cidr = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dia 1 - CIDR",
        help_text="Dia de inserção do CIDR (se aplicável)"
    )
    dia_pgf2a = models.IntegerField(
        default=7,
        verbose_name="Dia 7 - PGF2α",
        help_text="Dia de aplicação de PGF2α"
    )
    dia_retirada_cidr = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dia 7 - Retirada CIDR",
        help_text="Dia de retirada do CIDR (se aplicável)"
    )
    dia_gnrh_final = models.IntegerField(
        default=9,
        verbose_name="Dia 9 - GnRH Final",
        help_text="Dia da segunda aplicação de GnRH"
    )
    dia_iatf = models.IntegerField(
        default=10,
        verbose_name="Dia 10 - IATF",
        help_text="Dia da inseminação"
    )
    
    # Taxa de prenhez esperada
    taxa_prenhez_esperada = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00,
        verbose_name="Taxa de Prenhez Esperada (%)"
    )
    
    # Custos médios
    custo_protocolo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo Médio do Protocolo (R$)"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='protocolos_iatf',
        verbose_name="Propriedade",
        help_text="Protocolo específico da propriedade (ou global se null)"
    )
    
    class Meta:
        verbose_name = "Protocolo IATF"
        verbose_name_plural = "Protocolos IATF"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    @property
    def duracao_dias(self):
        """Duração total do protocolo em dias"""
        return self.dia_iatf


# ============================================================================
# SÊMEN
# ============================================================================

class TouroSemen(models.Model):
    """Cadastro de touros para sêmen"""
    TIPO_SEMEN_CHOICES = [
        ('CONVENCIONAL', 'Convencional'),
        ('SEXADO', 'Sexado'),
        ('IVF', 'In Vitro Fertilization'),
    ]
    
    numero_touro = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número do Touro"
    )
    nome_touro = models.CharField(max_length=200, verbose_name="Nome do Touro")
    raca = models.CharField(max_length=50, verbose_name="Raça")
    registro = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Registro Genealógico"
    )
    tipo_semen = models.CharField(
        max_length=20,
        choices=TIPO_SEMEN_CHOICES,
        default='CONVENCIONAL',
        verbose_name="Tipo de Sêmen"
    )
    
    # Características
    deposito_genetico = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Depósito Genético"
    )
    avaliacao_genetica = models.TextField(
        blank=True,
        null=True,
        verbose_name="Avaliação Genética"
    )
    
    # Preços
    preco_dose = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Preço por Dose (R$)"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Touro para Sêmen"
        verbose_name_plural = "Touros para Sêmen"
        ordering = ['nome_touro', 'numero_touro']
    
    def __str__(self):
        return f"{self.numero_touro} - {self.nome_touro} ({self.raca})"


class LoteSemen(models.Model):
    """Lotes de sêmen adquiridos"""
    STATUS_CHOICES = [
        ('ESTOQUE', 'Em Estoque'),
        ('RESERVADO', 'Reservado'),
        ('USADO', 'Usado'),
        ('VENCIDO', 'Vencido'),
        ('DESCARTADO', 'Descartado'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='lotes_semen',
        verbose_name="Propriedade"
    )
    touro = models.ForeignKey(
        TouroSemen,
        on_delete=models.CASCADE,
        related_name='lotes',
        verbose_name="Touro"
    )
    numero_lote = models.CharField(
        max_length=50,
        verbose_name="Número do Lote"
    )
    numero_doses = models.IntegerField(
        default=1,
        verbose_name="Número de Doses"
    )
    doses_utilizadas = models.IntegerField(
        default=0,
        verbose_name="Doses Utilizadas"
    )
    doses_disponiveis = models.IntegerField(
        default=0,
        verbose_name="Doses Disponíveis",
        help_text="Calculado automaticamente"
    )
    
    # Datas
    data_aquisicao = models.DateField(verbose_name="Data de Aquisição")
    data_validade = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Validade"
    )
    
    # Valores
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
    
    # Armazenamento
    localizacao = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Localização",
        help_text="Local de armazenamento (nitrogênio, etc.)"
    )
    temperatura_armazenamento = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Temperatura de Armazenamento",
        help_text="Ex: -196°C (nitrogênio líquido)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ESTOQUE',
        verbose_name="Status"
    )
    
    fornecedor = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Fornecedor"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Lote de Sêmen"
        verbose_name_plural = "Lotes de Sêmen"
        ordering = ['-data_aquisicao', 'touro']
        unique_together = ['numero_lote', 'propriedade']
    
    def __str__(self):
        return f"Lote {self.numero_lote} - {self.touro.nome_touro} - {self.doses_disponiveis} doses"
    
    def save(self, *args, **kwargs):
        # Calcular doses disponíveis
        self.doses_disponiveis = self.numero_doses - self.doses_utilizadas
        
        # Calcular valor total
        if self.numero_doses and self.preco_unitario:
            self.valor_total = Decimal(str(self.numero_doses)) * self.preco_unitario
        
        # Atualizar status
        if self.doses_disponiveis <= 0:
            self.status = 'USADO'
        elif self.data_validade and self.data_validade < date.today():
            self.status = 'VENCIDO'
        elif self.doses_disponiveis > 0:
            self.status = 'ESTOQUE'
        
        super().save(*args, **kwargs)


# ============================================================================
# LOTE IATF
# ============================================================================

class LoteIATF(models.Model):
    """Lote de IATF (grupo de animais inseminados juntos)"""
    STATUS_CHOICES = [
        ('PLANEJADO', 'Planejado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='lotes_iatf',
        verbose_name="Propriedade"
    )
    estacao_monta = models.ForeignKey(
        'EstacaoMonta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lotes_iatf',
        verbose_name="Estação de Monta"
    )
    
    # Dados do Lote
    nome_lote = models.CharField(max_length=200, verbose_name="Nome do Lote")
    protocolo = models.ForeignKey(
        ProtocoloIATF,
        on_delete=models.CASCADE,
        related_name='lotes_iatf',
        verbose_name="Protocolo"
    )
    categoria_animais = models.ManyToManyField(
        CategoriaAnimal,
        blank=True,
        related_name='lotes_iatf',
        verbose_name="Categorias de Vacas",
        help_text="Categorias de animais incluídas neste lote (ex.: Matrizes, Novilhas)."
    )
    score_reprodutivo = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Score Reprodutivo (%)",
        help_text="Avaliação geral do lote antes do protocolo (0 a 100%)."
    )
    
    # Datas
    data_inicio = models.DateField(verbose_name="Data de Início do Protocolo")
    data_iatf = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da IATF",
        help_text="Calculado automaticamente baseado no protocolo"
    )
    
    # Animais
    numero_animais = models.IntegerField(
        default=0,
        verbose_name="Número de Animais"
    )
    animais_inseminados = models.IntegerField(
        default=0,
        verbose_name="Animais Inseminados"
    )
    
    # Sêmen
    touro_semen = models.ForeignKey(
        TouroSemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lotes_iatf',
        verbose_name="Touro (Sêmen)"
    )
    lote_semen = models.ForeignKey(
        LoteSemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lotes_iatf',
        verbose_name="Lote de Sêmen"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PLANEJADO',
        verbose_name="Status"
    )
    
    # Custos
    custo_medicamentos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo de Medicamentos (R$)"
    )
    custo_semen = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo de Sêmen (R$)"
    )
    custo_mao_obra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo de Mão de Obra (R$)"
    )
    custo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Custo Total (R$)"
    )
    inseminador_padrao = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lotes_iatf_inseminador',
        verbose_name="Inseminador Padrão"
    )
    
    # Resultados
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
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lotes_iatf_responsavel',
        verbose_name="Responsável"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Lote de IATF"
        verbose_name_plural = "Lotes de IATF"
        ordering = ['-data_inicio', 'nome_lote']
    
    def __str__(self):
        return f"{self.nome_lote} - {self.data_inicio} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Calcular data da IATF baseado no protocolo
        if self.protocolo and self.data_inicio:
            self.data_iatf = self.data_inicio + timedelta(days=self.protocolo.dia_iatf)
        
        # Calcular custo total
        self.custo_total = (
            self.custo_medicamentos +
            self.custo_semen +
            self.custo_mao_obra
        )
        
        # Calcular taxa de prenhez
        if self.numero_animais > 0 and self.numero_prenhezes > 0:
            self.taxa_prenhez = (Decimal(str(self.numero_prenhezes)) / Decimal(str(self.numero_animais))) * 100
        
        super().save(*args, **kwargs)

    def gerar_etapas_padrao(self, user_padrao=None):
        """
        Gera etapas padrão (D0, D8, D10) caso ainda não existam registros
        """
        if not hasattr(self, 'etapas'):
            return

        etapas_existentes = set(self.etapas.values_list('dia_relativo', flat=True))
        etapas_padrao = [
            {
                'nome': 'Dia 0 - Início do Protocolo',
                'dia': 0,
                'medicamento_padrao': 'GnRH / Implante',
                'descricao': 'Aplicação inicial e inserção de implante conforme protocolo.'
            },
            {
                'nome': 'Dia 8 - Retirada Implante',
                'dia': self.protocolo.dia_pgf2a if self.protocolo else 8,
                'medicamento_padrao': 'PGF2α / Retirada Implante',
                'descricao': 'Aplicar PGF2α e retirar implante, repetir manejos conforme protocolo.'
            },
            {
                'nome': 'Dia 10 - Inseminação',
                'dia': self.protocolo.dia_iatf if self.protocolo else 10,
                'medicamento_padrao': 'IA',
                'descricao': 'Realizar inseminação artificial em tempo fixo.'
            },
        ]

        for etapa in etapas_padrao:
            if etapa['dia'] in etapas_existentes:
                continue
            data_prevista = self.data_inicio + timedelta(days=etapa['dia'])
            self.etapas.create(
                nome_etapa=etapa['nome'],
                dia_relativo=etapa['dia'],
                data_prevista=data_prevista,
                medicamento_planejado=etapa['medicamento_padrao'],
                descricao_planejada=etapa['descricao'],
                responsavel_planejado=user_padrao or self.responsavel or self.inseminador_padrao
            )


class EtapaLoteIATF(models.Model):
    """Etapas planejadas e executadas de um lote IATF"""
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('AGENDADA', 'Agendada'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]

    lote = models.ForeignKey(
        LoteIATF,
        on_delete=models.CASCADE,
        related_name='etapas',
        verbose_name="Lote IATF"
    )
    nome_etapa = models.CharField(max_length=150, verbose_name="Nome da Etapa")
    codigo_etapa = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        verbose_name="Código da Etapa",
        help_text="Identificador curto (ex.: D0, D8, D10)."
    )
    dia_relativo = models.IntegerField(
        verbose_name="Dia Relativo",
        help_text="Dia em relação ao início do protocolo (Ex.: 0, 8, 10)."
    )
    data_prevista = models.DateField(verbose_name="Data Prevista")
    hora_prevista = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Horário Previsto"
    )
    medicamento_planejado = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Medicamento Planejado"
    )
    descricao_planejada = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição / Procedimentos"
    )
    responsavel_planejado = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etapas_iatf_planejadas',
        verbose_name="Responsável Planejado"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name="Status"
    )
    data_execucao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Execução"
    )
    hora_execucao = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de Execução"
    )
    responsavel_execucao = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etapas_iatf_executadas',
        verbose_name="Responsável Execução"
    )
    inseminador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etapas_iatf_inseminador',
        verbose_name="Inseminador"
    )
    touro_semen = models.ForeignKey(
        TouroSemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etapas_iatf',
        verbose_name="Touro Utilizado"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Etapa de Lote IATF"
        verbose_name_plural = "Etapas de Lote IATF"
        ordering = ['lote', 'dia_relativo', 'data_prevista']

    def __str__(self):
        return f"{self.lote.nome_lote} - {self.nome_etapa} (Dia {self.dia_relativo})"

    @property
    def esta_atrasada(self):
        if self.status in ['CONCLUIDA', 'CANCELADA']:
            return False
        if self.data_prevista and date.today() > self.data_prevista:
            return True
        return False


# ============================================================================
# IATF INDIVIDUAL EXPANDIDO
# ============================================================================

class IATFIndividual(models.Model):
    """IATF individual expandido com todas as informações"""
    STATUS_CHOICES = [
        ('PROGRAMADA', 'Programada'),
        ('PROTOCOLO_INICIADO', 'Protocolo Iniciado'),
        ('DIA_0_GNRH', 'Dia 0 - GnRH Aplicado'),
        ('DIA_7_PGF2A', 'Dia 7 - PGF2α Aplicado'),
        ('DIA_9_GNRH', 'Dia 9 - GnRH Aplicado'),
        ('REALIZADA', 'IATF Realizada'),
        ('CANCELADA', 'Cancelada'),
        ('FALHOU', 'Falhou'),
    ]
    
    RESULTADO_CHOICES = [
        ('PENDENTE', 'Pendente Diagnóstico'),
        ('PREMIDA', 'Prenhez Confirmada'),
        ('VAZIA', 'Vazia'),
        ('ABORTO', 'Aborto'),
        ('REPETICAO', 'Repetição de Cio'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='iatfs_individuais',
        verbose_name="Propriedade"
    )
    lote_iatf = models.ForeignKey(
        LoteIATF,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs',
        verbose_name="Lote de IATF"
    )
    estacao_monta = models.ForeignKey(
        'EstacaoMonta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs_individuais',
        verbose_name="Estação de Monta"
    )
    animal_individual = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='iatfs_individuais',
        verbose_name="Animal"
    )
    
    # Protocolo
    protocolo = models.ForeignKey(
        ProtocoloIATF,
        on_delete=models.CASCADE,
        related_name='iatfs',
        verbose_name="Protocolo"
    )
    
    # Datas do Protocolo
    data_inicio_protocolo = models.DateField(verbose_name="Data de Início do Protocolo")
    data_dia_0_gnrh = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data Dia 0 - GnRH"
    )
    data_dia_7_pgf2a = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data Dia 7 - PGF2α"
    )
    data_dia_9_gnrh = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data Dia 9 - GnRH Final"
    )
    data_iatf = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da IATF"
    )
    data_iatf_realizada = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da IATF Realizada",
        help_text="Data/hora exata da inseminação"
    )
    hora_iatf = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora da IATF"
    )
    
    # Sêmen
    touro_semen = models.ForeignKey(
        TouroSemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs',
        verbose_name="Touro (Sêmen)"
    )
    lote_semen = models.ForeignKey(
        LoteSemen,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs',
        verbose_name="Lote de Sêmen Utilizado"
    )
    numero_dose = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Número da Dose"
    )
    
    # Status e Resultado
    status = models.CharField(
        max_length=30,
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
    metodo_diagnostico = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Método de Diagnóstico",
        help_text="Ex: Palpação Retal, Ultrassom, etc."
    )
    diagnostico_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs_diagnosticadas',
        verbose_name="Diagnóstico por"
    )
    
    # Condição do Animal
    condicao_corporal = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Condição Corporal (1-5)",
        help_text="Escala de 1 a 5"
    )
    peso_kg = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso (kg)"
    )
    dias_vazia = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dias Vazia",
        help_text="Dias desde o último parto/nascimento"
    )
    
    # Custos
    custo_protocolo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo do Protocolo (R$)"
    )
    custo_semen = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo do Sêmen (R$)"
    )
    custo_inseminacao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo da Inseminação (R$)"
    )
    custo_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Custo Total (R$)"
    )
    
    # Responsáveis
    inseminador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs_individuais_realizadas',
        verbose_name="Inseminador"
    )
    veterinario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iatfs_individuais_veterinario',
        verbose_name="Veterinário Responsável"
    )
    
    # Observações
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    observacoes_protocolo = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações do Protocolo"
    )
    observacoes_diagnostico = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações do Diagnóstico"
    )
    
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "IATF Individual"
        verbose_name_plural = "IATFs Individuais"
        ordering = ['-data_inicio_protocolo', 'animal_individual']
        indexes = [
            models.Index(fields=['animal_individual', 'data_iatf']),
            models.Index(fields=['lote_iatf', 'status']),
            models.Index(fields=['resultado', 'data_diagnostico']),
        ]
    
    def __str__(self):
        return f"{self.animal_individual.numero_brinco} - {self.data_inicio_protocolo} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        # Calcular datas do protocolo
        if self.protocolo and self.data_inicio_protocolo:
            if not self.data_dia_0_gnrh:
                self.data_dia_0_gnrh = self.data_inicio_protocolo + timedelta(days=self.protocolo.dia_gnrh)
            if not self.data_dia_7_pgf2a:
                self.data_dia_7_pgf2a = self.data_inicio_protocolo + timedelta(days=self.protocolo.dia_pgf2a)
            if not self.data_dia_9_gnrh:
                self.data_dia_9_gnrh = self.data_inicio_protocolo + timedelta(days=self.protocolo.dia_gnrh_final)
            if not self.data_iatf:
                self.data_iatf = self.data_inicio_protocolo + timedelta(days=self.protocolo.dia_iatf)
        
        # Calcular custo total
        self.custo_total = (
            self.custo_protocolo +
            self.custo_semen +
            self.custo_inseminacao
        )
        
        super().save(*args, **kwargs)
    
    @property
    def dias_ate_diagnostico(self):
        """Dias até o diagnóstico de prenhez"""
        if self.data_iatf and self.data_diagnostico:
            return (self.data_diagnostico - self.data_iatf).days
        return None
    
    @property
    def custo_por_prenhez(self):
        """Custo por prenhez (se confirmada)"""
        if self.resultado == 'PREMIDA' and self.custo_total > 0:
            return self.custo_total
        return None


# ============================================================================
# APLICAÇÕES DE MEDICAMENTOS
# ============================================================================

class AplicacaoMedicamentoIATF(models.Model):
    """Aplicações de medicamentos durante o protocolo IATF"""
    TIPO_MEDICAMENTO_CHOICES = [
        ('GnRH', 'GnRH'),
        ('PGF2A', 'PGF2α'),
        ('CIDR', 'CIDR'),
        ('E2', 'Estradiol'),
        ('OUTROS', 'Outros'),
    ]
    
    iatf = models.ForeignKey(
        IATFIndividual,
        on_delete=models.CASCADE,
        related_name='aplicacoes_medicamentos',
        verbose_name="IATF"
    )
    
    tipo_medicamento = models.CharField(
        max_length=20,
        choices=TIPO_MEDICAMENTO_CHOICES,
        verbose_name="Tipo de Medicamento"
    )
    nome_medicamento = models.CharField(
        max_length=200,
        verbose_name="Nome do Medicamento"
    )
    dosagem = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Dosagem",
        help_text="Ex: 2ml, 100mg"
    )
    
    # Data e hora
    data_aplicacao = models.DateField(verbose_name="Data de Aplicação")
    hora_aplicacao = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora de Aplicação"
    )
    
    # Dia do protocolo
    dia_protocolo = models.IntegerField(
        verbose_name="Dia do Protocolo",
        help_text="Dia 0, 7, 9, etc."
    )
    
    # Responsável
    aplicado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Aplicado por"
    )
    
    # Validação
    aplicado_corretamente = models.BooleanField(
        default=True,
        verbose_name="Aplicado Corretamente"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Aplicação de Medicamento IATF"
        verbose_name_plural = "Aplicações de Medicamentos IATF"
        ordering = ['iatf', 'dia_protocolo', 'data_aplicacao']
    
    def __str__(self):
        return f"{self.iatf.animal_individual.numero_brinco} - {self.get_tipo_medicamento_display()} - Dia {self.dia_protocolo}"


# ============================================================================
# CALENDÁRIO IATF
# ============================================================================

class CalendarioIATF(models.Model):
    """Calendário de IATF da propriedade"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='calendarios_iatf',
        verbose_name="Propriedade"
    )
    
    nome = models.CharField(max_length=200, verbose_name="Nome do Calendário")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_fim = models.DateField(verbose_name="Data de Término")
    
    # Configurações
    intervalo_entre_lotes = models.IntegerField(
        default=14,
        verbose_name="Intervalo entre Lotes (dias)",
        help_text="Dias entre cada lote de IATF"
    )
    protocolo_padrao = models.ForeignKey(
        ProtocoloIATF,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Protocolo Padrão"
    )
    
    # Estatísticas
    numero_lotes_planejados = models.IntegerField(
        default=0,
        verbose_name="Número de Lotes Planejados"
    )
    numero_lotes_realizados = models.IntegerField(
        default=0,
        verbose_name="Número de Lotes Realizados"
    )
    
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Calendário IATF"
        verbose_name_plural = "Calendários IATF"
        ordering = ['-data_inicio', 'propriedade']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.nome} ({self.data_inicio} a {self.data_fim})"
    
    def calcular_numero_lotes(self):
        """Calcula número de lotes possíveis no período"""
        if self.data_inicio and self.data_fim and self.intervalo_entre_lotes:
            delta = self.data_fim - self.data_inicio
            if self.protocolo_padrao:
                duracao_protocolo = self.protocolo_padrao.duracao_dias
            else:
                duracao_protocolo = 10  # Padrão
            
            # Número de lotes = (período total) / (intervalo + duração)
            lotes = delta.days // (self.intervalo_entre_lotes + duracao_protocolo)
            self.numero_lotes_planejados = max(0, lotes)
            return lotes
        return 0
    
    def save(self, *args, **kwargs):
        self.calcular_numero_lotes()
        super().save(*args, **kwargs)

