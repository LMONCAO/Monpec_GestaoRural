# -*- coding: utf-8 -*-
"""
Modelos para Sistema de Relatórios Customizados
Permite que usuários criem e salvem relatórios personalizados
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import json


class RelatorioCustomizado(models.Model):
    """Modelo para armazenar relatórios customizados criados pelos usuários"""
    
    TIPO_PDF = 'PDF'
    TIPO_EXCEL = 'EXCEL'
    TIPO_HTML = 'HTML'
    
    TIPO_CHOICES = [
        (TIPO_PDF, 'PDF'),
        (TIPO_EXCEL, 'Excel'),
        (TIPO_HTML, 'HTML'),
    ]
    
    MODULO_PECUARIA = 'PECUARIA'
    MODULO_FINANCEIRO = 'FINANCEIRO'
    MODULO_NUTRICAO = 'NUTRICAO'
    MODULO_OPERACOES = 'OPERACOES'
    MODULO_COMPRAS = 'COMPRAS'
    MODULO_IATF = 'IATF'
    MODULO_RASTREABILIDADE = 'RASTREABILIDADE'
    MODULO_CONSOLIDADO = 'CONSOLIDADO'
    
    MODULO_CHOICES = [
        (MODULO_PECUARIA, 'Pecuária'),
        (MODULO_FINANCEIRO, 'Financeiro'),
        (MODULO_NUTRICAO, 'Nutrição'),
        (MODULO_OPERACOES, 'Operações'),
        (MODULO_COMPRAS, 'Compras'),
        (MODULO_IATF, 'IATF'),
        (MODULO_RASTREABILIDADE, 'Rastreabilidade'),
        (MODULO_CONSOLIDADO, 'Consolidado'),
    ]
    
    # Informações básicas
    nome = models.CharField(max_length=200, verbose_name="Nome do Relatório")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    propriedade = models.ForeignKey(
        'Propriedade',
        on_delete=models.CASCADE,
        related_name='relatorios_customizados',
        verbose_name="Propriedade"
    )
    usuario_criador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='relatorios_criados',
        verbose_name="Usuário Criador"
    )
    
    # Configurações do relatório
    modulo = models.CharField(
        max_length=50,
        choices=MODULO_CHOICES,
        verbose_name="Módulo"
    )
    tipo_exportacao = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default=TIPO_HTML,
        verbose_name="Tipo de Exportação"
    )
    
    # Campos selecionados (JSON)
    campos_selecionados = models.JSONField(
        default=list,
        verbose_name="Campos Selecionados",
        help_text="Lista de campos que serão exibidos no relatório"
    )
    
    # Filtros (JSON)
    filtros = models.JSONField(
        default=dict,
        verbose_name="Filtros",
        help_text="Filtros aplicados ao relatório"
    )
    
    # Agrupamentos (JSON)
    agrupamentos = models.JSONField(
        default=list,
        verbose_name="Agrupamentos",
        help_text="Campos para agrupar os dados"
    )
    
    # Ordenação (JSON)
    ordenacao = models.JSONField(
        default=list,
        verbose_name="Ordenação",
        help_text="Campos e direção de ordenação"
    )
    
    # Configurações de formatação (JSON)
    formatacao = models.JSONField(
        default=dict,
        verbose_name="Formatação",
        help_text="Configurações de formatação (cores, estilos, etc.)"
    )
    
    # Configurações de template
    template_personalizado = models.TextField(
        blank=True,
        null=True,
        verbose_name="Template Personalizado",
        help_text="HTML customizado para o relatório (opcional)"
    )
    
    # Metadados
    compartilhado = models.BooleanField(
        default=False,
        verbose_name="Compartilhado",
        help_text="Se o relatório pode ser usado por outros usuários da propriedade"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    ultima_execucao = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Última Execução"
    )
    total_execucoes = models.PositiveIntegerField(
        default=0,
        verbose_name="Total de Execuções"
    )
    
    class Meta:
        verbose_name = "Relatório Customizado"
        verbose_name_plural = "Relatórios Customizados"
        ordering = ['-data_atualizacao', 'nome']
        unique_together = [['propriedade', 'nome', 'usuario_criador']]
    
    def __str__(self):
        return f"{self.nome} - {self.get_modulo_display()}"
    
    def incrementar_execucao(self):
        """Incrementa o contador de execuções"""
        from django.utils import timezone
        self.total_execucoes += 1
        self.ultima_execucao = timezone.now()
        self.save(update_fields=['total_execucoes', 'ultima_execucao'])
    
    def get_campos_selecionados_list(self):
        """Retorna lista de campos selecionados"""
        if isinstance(self.campos_selecionados, list):
            return self.campos_selecionados
        return []
    
    def get_filtros_dict(self):
        """Retorna dicionário de filtros"""
        if isinstance(self.filtros, dict):
            return self.filtros
        return {}
    
    def get_agrupamentos_list(self):
        """Retorna lista de agrupamentos"""
        if isinstance(self.agrupamentos, list):
            return self.agrupamentos
        return []
    
    def get_ordenacao_list(self):
        """Retorna lista de ordenação"""
        if isinstance(self.ordenacao, list):
            return self.ordenacao
        return []


class TemplateRelatorio(models.Model):
    """Templates pré-definidos de relatórios que podem ser usados como base"""
    
    nome = models.CharField(max_length=200, verbose_name="Nome do Template")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    modulo = models.CharField(
        max_length=50,
        choices=RelatorioCustomizado.MODULO_CHOICES,
        verbose_name="Módulo"
    )
    
    # Configuração do template (JSON)
    configuracao = models.JSONField(
        default=dict,
        verbose_name="Configuração",
        help_text="Configuração completa do template (campos, filtros, etc.)"
    )
    
    # Template HTML
    template_html = models.TextField(
        blank=True,
        null=True,
        verbose_name="Template HTML",
        help_text="HTML do template"
    )
    
    # Metadados
    publico = models.BooleanField(
        default=True,
        verbose_name="Público",
        help_text="Se o template está disponível para todos"
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Criação"
    )
    
    class Meta:
        verbose_name = "Template de Relatório"
        verbose_name_plural = "Templates de Relatórios"
        ordering = ['modulo', 'nome']
    
    def __str__(self):
        return f"{self.nome} - {self.get_modulo_display()}"






