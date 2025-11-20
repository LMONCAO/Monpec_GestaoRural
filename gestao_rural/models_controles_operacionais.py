# -*- coding: utf-8 -*-
"""
Modelos para Controles Operacionais
- Distribuição de sal/ração no pasto
- Controle de cochos
- Gestão de pastagens com KML
- Abastecimento
- Manutenção de frota
- Fábrica de ração
- Empreiteiros
- Funcionários
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from .models import Propriedade, CategoriaAnimal, AnimalIndividual


# ============================================================================
# CONTROLE DE DISTRIBUIÇÃO NO PASTO
# ============================================================================

class TipoDistribuicao(models.Model):
    """Tipos de distribuição (sal, ração, suplemento)"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    unidade_medida = models.CharField(
        max_length=20,
        default='KG',
        verbose_name="Unidade de Medida"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Tipo de Distribuição"
        verbose_name_plural = "Tipos de Distribuição"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class DistribuicaoPasto(models.Model):
    """Controle de distribuição de sal/ração/suplemento no pasto"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='distribuicoes_pasto',
        verbose_name="Propriedade"
    )
    pastagem = models.ForeignKey(
        'Pastagem',
        on_delete=models.CASCADE,
        related_name='distribuicoes',
        verbose_name="Pastagem/Piquete"
    )
    tipo_distribuicao = models.ForeignKey(
        TipoDistribuicao,
        on_delete=models.CASCADE,
        verbose_name="Tipo de Distribuição"
    )
    data_distribuicao = models.DateField(verbose_name="Data da Distribuição")
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Quantidade"
    )
    quantidade_por_animal = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Quantidade por Animal",
        help_text="Calculado automaticamente"
    )
    numero_animais = models.IntegerField(
        default=0,
        verbose_name="Número de Animais no Piquete"
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
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_registro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Registro")
    
    class Meta:
        verbose_name = "Distribuição no Pasto"
        verbose_name_plural = "Distribuições no Pasto"
        ordering = ['-data_distribuicao', 'pastagem']
    
    def __str__(self):
        return f"{self.pastagem.nome} - {self.tipo_distribuicao.nome} - {self.data_distribuicao}"
    
    def save(self, *args, **kwargs):
        # Calcular quantidade por animal
        if self.numero_animais > 0 and self.quantidade:
            self.quantidade_por_animal = self.quantidade / Decimal(str(self.numero_animais))
        
        # Calcular valor total
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
        
        super().save(*args, **kwargs)


# ============================================================================
# CONTROLE DE COCHOS
# ============================================================================

class Cocho(models.Model):
    """Cadastro de cochos da propriedade"""
    TIPO_COCHO_CHOICES = [
        ('SAL', 'Cocho de Sal'),
        ('RACAO', 'Cocho de Ração'),
        ('AGUA', 'Bebedouro'),
        ('MISTO', 'Misto'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('INATIVO', 'Inativo'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='cochos',
        verbose_name="Propriedade"
    )
    pastagem = models.ForeignKey(
        'Pastagem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cochos',
        verbose_name="Pastagem/Piquete"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome/Identificação do Cocho")
    tipo_cocho = models.CharField(
        max_length=20,
        choices=TIPO_COCHO_CHOICES,
        verbose_name="Tipo de Cocho"
    )
    capacidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Capacidade",
        help_text="Capacidade em kg ou litros"
    )
    unidade_capacidade = models.CharField(
        max_length=10,
        default='KG',
        verbose_name="Unidade"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ATIVO',
        verbose_name="Status"
    )
    coordenadas = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Coordenadas GPS",
        help_text="Latitude, Longitude (para mapas)"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Cocho"
        verbose_name_plural = "Cochos"
        ordering = ['propriedade', 'pastagem', 'nome']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.nome}"


class ControleCocho(models.Model):
    """Controle diário de consumo nos cochos"""
    cocho = models.ForeignKey(
        Cocho,
        on_delete=models.CASCADE,
        related_name='controles',
        verbose_name="Cocho"
    )
    data = models.DateField(verbose_name="Data")
    hora = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Hora",
        help_text="Hora do registro (opcional)"
    )
    
    # Quantidades
    quantidade_abastecida = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Quantidade Abastecida"
    )
    quantidade_restante = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Quantidade Restante",
        help_text="Quantidade que sobrou no cocho"
    )
    quantidade_consumida = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Quantidade Consumida",
        help_text="Calculado automaticamente"
    )
    
    # Informações do piquete
    numero_animais = models.IntegerField(
        default=0,
        verbose_name="Número de Animais no Piquete"
    )
    consumo_por_animal = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Consumo por Animal",
        help_text="Calculado automaticamente"
    )
    
    # Valores
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Unitário (R$)"
    )
    valor_total_consumido = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Total Consumido (R$)"
    )
    
    # Observações
    condicao_cocho = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Condição do Cocho",
        help_text="Bom, Regular, Ruim, Necessita Limpeza"
    )
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
        verbose_name = "Controle de Cocho"
        verbose_name_plural = "Controles de Cochos"
        ordering = ['-data', '-hora', 'cocho']
        unique_together = ['cocho', 'data', 'hora']
    
    def __str__(self):
        return f"{self.cocho.nome} - {self.data}"
    
    def save(self, *args, **kwargs):
        # Calcular quantidade consumida
        if self.quantidade_abastecida and self.quantidade_restante is not None:
            self.quantidade_consumida = self.quantidade_abastecida - self.quantidade_restante
        
        # Calcular consumo por animal
        if self.numero_animais > 0 and self.quantidade_consumida:
            self.consumo_por_animal = self.quantidade_consumida / Decimal(str(self.numero_animais))
        
        # Calcular valor total consumido
        if self.quantidade_consumida and self.valor_unitario:
            self.valor_total_consumido = self.quantidade_consumida * self.valor_unitario
        
        super().save(*args, **kwargs)


# ============================================================================
# GESTÃO DE PASTAGENS COM KML
# ============================================================================

class ArquivoKML(models.Model):
    """Arquivo KML importado da fazenda"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='arquivos_kml',
        verbose_name="Propriedade"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome do Arquivo")
    arquivo = models.FileField(
        upload_to='kml/fazendas/',
        verbose_name="Arquivo KML"
    )
    data_importacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Importação")
    importado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Importado por"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Arquivo KML"
        verbose_name_plural = "Arquivos KML"
        ordering = ['-data_importacao']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.nome}"


class Pastagem(models.Model):
    """Cadastro de pastagens/piquetes com suporte a KML"""
    STATUS_CHOICES = [
        ('EM_USO', 'Em Uso'),
        ('DESCANSO', 'Descanso'),
        ('REFORMA', 'Reforma'),
        ('PLANTIO', 'Em Plantio'),
    ]
    
    TIPO_PASTAGEM_CHOICES = [
        ('BRACHIARIA', 'Braquiária'),
        ('PANICUM', 'Panicum'),
        ('CYNODON', 'Cynodon'),
        ('UROCHLOA', 'Urochloa'),
        ('OUTROS', 'Outros'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='pastagens',
        verbose_name="Propriedade"
    )
    nome = models.CharField(max_length=200, verbose_name="Nome do Piquete/Pastagem")
    tipo_pastagem = models.CharField(
        max_length=20,
        choices=TIPO_PASTAGEM_CHOICES,
        default='BRACHIARIA',
        verbose_name="Tipo de Pastagem"
    )
    
    # Área (pode ser calculada do KML ou informada manualmente)
    area_ha = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name="Área (ha)",
        help_text="Calculada automaticamente do KML ou informada manualmente"
    )
    
    # Coordenadas do polígono (do KML)
    coordenadas_kml = models.TextField(
        blank=True,
        null=True,
        verbose_name="Coordenadas KML",
        help_text="Polígono extraído do KML (latitude,longitude)"
    )
    
    # Capacidade de suporte
    capacidade_suporte = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Capacidade de Suporte (UA/ha)",
        help_text="Unidades Animal por hectare"
    )
    
    # Status e datas
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EM_USO',
        verbose_name="Status"
    )
    data_plantio = models.DateField(null=True, blank=True, verbose_name="Data de Plantio")
    data_ultima_reforma = models.DateField(null=True, blank=True, verbose_name="Data da Última Reforma")
    
    # Relacionamento com KML
    arquivo_kml = models.ForeignKey(
        ArquivoKML,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pastagens',
        verbose_name="Arquivo KML de Origem"
    )
    
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Pastagem/Piquete"
        verbose_name_plural = "Pastagens/Piquetes"
        ordering = ['propriedade', 'nome']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.nome} ({self.area_ha} ha)"
    
    def calcular_area_do_kml(self):
        """Calcula área do polígono KML em hectares"""
        if not self.coordenadas_kml:
            return None
        
        try:
            # Parse das coordenadas do KML
            # Formato esperado: "lat1,lon1 lat2,lon2 ..."
            coords = self.coordenadas_kml.strip().split()
            if len(coords) < 3:
                return None
            
            # Converter coordenadas e calcular área usando fórmula de Shoelace
            from math import radians, sin, cos
            
            pontos = []
            for coord in coords:
                lon, lat = map(float, coord.split(','))
                pontos.append((radians(lat), radians(lon)))
            
            # Fórmula de Shoelace para área de polígono esférico
            # Aproximação usando fórmula de área de polígono esférico
            area_m2 = 0
            for i in range(len(pontos)):
                j = (i + 1) % len(pontos)
                area_m2 += (pontos[j][1] - pontos[i][1]) * (
                    2 + sin(pontos[i][0]) + sin(pontos[j][0])
                )
            
            area_m2 = abs(area_m2) * 6371000**2 / 2  # Raio da Terra em metros
            area_ha = area_m2 / 10000  # Converter para hectares
            
            return Decimal(str(round(area_ha, 4)))
        except (ValueError, TypeError, ZeroDivisionError, AttributeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Erro ao calcular área do polígono: {e}")
            return None


class RotacaoPastagem(models.Model):
    """Controle de rotação de pastagens"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='rotacoes_pastagem',
        verbose_name="Propriedade"
    )
    pastagem = models.ForeignKey(
        Pastagem,
        on_delete=models.CASCADE,
        related_name='rotacoes',
        verbose_name="Pastagem/Piquete"
    )
    data_entrada = models.DateField(verbose_name="Data de Entrada")
    data_saida = models.DateField(verbose_name="Data de Saída")
    animais_entrada = models.IntegerField(verbose_name="Número de Animais na Entrada")
    animais_saida = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Animais na Saída"
    )
    categoria_animal = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria de Animais"
    )
    dias_pastoreio = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dias de Pastoreio",
        help_text="Calculado automaticamente"
    )
    dias_descanso = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dias de Descanso Anteriores"
    )
    taxa_lotacao = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Taxa de Lotação (UA/ha)",
        help_text="Calculado automaticamente"
    )
    altura_entrada = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Altura na Entrada (cm)"
    )
    altura_saida = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Altura na Saída (cm)"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Rotação de Pastagem"
        verbose_name_plural = "Rotações de Pastagens"
        ordering = ['-data_entrada', 'pastagem']
    
    def __str__(self):
        return f"{self.pastagem.nome} - {self.data_entrada} a {self.data_saida}"
    
    def save(self, *args, **kwargs):
        # Calcular dias de pastoreio
        if self.data_entrada and self.data_saida:
            delta = self.data_saida - self.data_entrada
            self.dias_pastoreio = delta.days
        
        # Calcular taxa de lotação
        if self.pastagem.area_ha > 0 and self.animais_entrada > 0:
            # Converter número de animais para UA (assumindo 1 animal = 1 UA para simplificar)
            # Em produção real, usar tabela de conversão por categoria
            ua = self.animais_entrada
            self.taxa_lotacao = Decimal(str(ua)) / self.pastagem.area_ha
        
        super().save(*args, **kwargs)


class MonitoramentoPastagem(models.Model):
    """Monitoramento de condições das pastagens"""
    CONDICAO_CHOICES = [
        ('EXCELENTE', 'Excelente'),
        ('BOM', 'Bom'),
        ('REGULAR', 'Regular'),
        ('RUIM', 'Ruim'),
        ('MUITO_RUIM', 'Muito Ruim'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='monitoramentos_pastagem',
        verbose_name="Propriedade"
    )
    pastagem = models.ForeignKey(
        Pastagem,
        on_delete=models.CASCADE,
        related_name='monitoramentos',
        verbose_name="Pastagem/Piquete"
    )
    data = models.DateField(verbose_name="Data do Monitoramento")
    altura_pasto = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Altura do Pasto (cm)"
    )
    cobertura_vegetal = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Cobertura Vegetal (%)",
        help_text="Percentual de cobertura do solo"
    )
    capacidade_suporte_atual = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Capacidade de Suporte Atual (UA/ha)"
    )
    animais_em_pasto = models.IntegerField(
        default=0,
        verbose_name="Número de Animais em Pastoreio"
    )
    dias_descanso = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dias de Descanso"
    )
    condicao_pasto = models.CharField(
        max_length=20,
        choices=CONDICAO_CHOICES,
        null=True,
        blank=True,
        verbose_name="Condição do Pasto"
    )
    necessidade_manejo = models.BooleanField(
        default=False,
        verbose_name="Necessita Manejo"
    )
    necessidade_reforma = models.BooleanField(
        default=False,
        verbose_name="Necessita Reforma"
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
        verbose_name = "Monitoramento de Pastagem"
        verbose_name_plural = "Monitoramentos de Pastagens"
        ordering = ['-data', 'pastagem']
    
    def __str__(self):
        return f"{self.pastagem.nome} - {self.data}"


