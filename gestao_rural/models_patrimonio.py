"""
Modelos para gestão de Bens e Patrimônio
"""
from django.db import models
from decimal import Decimal


class TipoBem(models.Model):
    """Tipos de bens patrimoniais"""
    CATEGORIAS = [
        ('TERRA', 'Terras e Benfeitorias'),
        ('MAQUINA', 'Máquinas e Equipamentos'),
        ('VEICULO', 'Veículos'),
        ('INSTALACAO', 'Instalações e Construções'),
        ('ANIMAL', 'Animais de Trabalho'),
        ('OUTRO', 'Outros Bens'),
    ]
    
    nome = models.CharField('Nome', max_length=100)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIAS)
    descricao = models.TextField('Descrição', blank=True)
    vida_util_anos = models.IntegerField('Vida Útil (anos)', default=10)
    taxa_depreciacao = models.DecimalField('Taxa de Depreciação (%)', max_digits=5, decimal_places=2, default=10.00)
    
    class Meta:
        verbose_name = 'Tipo de Bem'
        verbose_name_plural = 'Tipos de Bens'
        ordering = ['categoria', 'nome']
    
    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"


class BemPatrimonial(models.Model):
    """Registro de bens patrimoniais"""
    propriedade = models.ForeignKey('Propriedade', on_delete=models.CASCADE, related_name='bens')
    tipo_bem = models.ForeignKey(TipoBem, on_delete=models.PROTECT)
    
    descricao = models.CharField('Descrição', max_length=200)
    data_aquisicao = models.DateField('Data de Aquisição')
    valor_aquisicao = models.DecimalField('Valor de Aquisição', max_digits=12, decimal_places=2)
    valor_residual = models.DecimalField('Valor Residual', max_digits=12, decimal_places=2, default=0)
    
    quantidade = models.IntegerField('Quantidade', default=1)
    estado_conservacao = models.CharField('Estado de Conservação', max_length=20,
        choices=[
            ('NOVO', 'Novo'),
            ('OTIMO', 'Ótimo'),
            ('BOM', 'Bom'),
            ('REGULAR', 'Regular'),
            ('RUIM', 'Ruim'),
        ],
        default='BOM'
    )
    
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Bem Patrimonial'
        verbose_name_plural = 'Bens Patrimoniais'
        ordering = ['-data_aquisicao']
    
    def __str__(self):
        return f"{self.descricao} - {self.tipo_bem.nome}"
    
    @property
    def valor_atual(self):
        """Calcula valor atual com depreciação"""
        from datetime import date
        anos_uso = Decimal(str((date.today() - self.data_aquisicao).days / 365))
        taxa_anual = self.tipo_bem.taxa_depreciacao / 100
        depreciacao_total = self.valor_aquisicao * taxa_anual * anos_uso
        valor_atual = self.valor_aquisicao - depreciacao_total
        return max(valor_atual, self.valor_residual)
    
    @property
    def depreciacao_acumulada(self):
        """Calcula depreciação acumulada"""
        return self.valor_aquisicao - self.valor_atual
    
    @property
    def percentual_depreciacao(self):
        """Percentual de depreciação"""
        if self.valor_aquisicao > 0:
            return (self.depreciacao_acumulada / self.valor_aquisicao) * 100
        return 0

