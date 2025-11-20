from django.db import models
from django.contrib.auth.models import User

class Proprietario(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cidade")
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name="Estado")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Proprietário"
        verbose_name_plural = "Proprietários"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    @property
    def area_total(self):
        return sum(prop.area for prop in self.propriedades.all())

class Propriedade(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Propriedade")
    proprietario = models.ForeignKey(Proprietario, on_delete=models.CASCADE, related_name='propriedades', verbose_name="Proprietário")
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Área (hectares)")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    matricula = models.CharField(max_length=100, blank=True, null=True, verbose_name="Matrícula")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.proprietario.nome}"

class ProjetoCredito(models.Model):
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('finalizado', 'Finalizado'),
    ]
    
    TIPO_CHOICES = [
        ('custeio', 'Custeio'),
        ('investimento', 'Investimento'),
        ('comercializacao', 'Comercialização'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='projetos', verbose_name="Propriedade")
    titulo = models.CharField(max_length=200, verbose_name="Título do Projeto")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Crédito")
    valor_solicitado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Solicitado (R$)")
    prazo_pagamento = models.IntegerField(verbose_name="Prazo (meses)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='rascunho', verbose_name="Status")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_vencimento = models.DateField(blank=True, null=True, verbose_name="Data de Vencimento")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Projeto de Crédito"
        verbose_name_plural = "Projetos de Crédito"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titulo} - {self.propriedade.nome}"
