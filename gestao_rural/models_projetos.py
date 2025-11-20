"""
Modelos para gestão de Projetos
"""
from django.db import models
from decimal import Decimal


class Projeto(models.Model):
    """Projetos de investimento e melhorias"""
    propriedade = models.ForeignKey('Propriedade', on_delete=models.CASCADE, related_name='projetos')
    
    nome = models.CharField('Nome do Projeto', max_length=200)
    descricao = models.TextField('Descrição')
    
    STATUS_CHOICES = [
        ('PLANEJAMENTO', 'Em Planejamento'),
        ('APROVADO', 'Aprovado'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
    ]
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='PLANEJAMENTO')
    
    TIPO_CHOICES = [
        ('INFRAESTRUTURA', 'Infraestrutura'),
        ('MAQUINAS', 'Máquinas e Equipamentos'),
        ('REBANHO', 'Expansão de Rebanho'),
        ('TECNOLOGIA', 'Tecnologia'),
        ('SUSTENTABILIDADE', 'Sustentabilidade'),
        ('OUTRO', 'Outro'),
    ]
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    
    data_inicio = models.DateField('Data de Início Prevista')
    data_conclusao_prevista = models.DateField('Data de Conclusão Prevista')
    data_conclusao_real = models.DateField('Data de Conclusão Real', null=True, blank=True)
    
    orcamento_previsto = models.DecimalField('Orçamento Previsto', max_digits=12, decimal_places=2)
    custo_realizado = models.DecimalField('Custo Realizado', max_digits=12, decimal_places=2, default=0)
    
    responsavel = models.CharField('Responsável', max_length=100, blank=True)
    prioridade = models.CharField('Prioridade', max_length=10,
        choices=[
            ('BAIXA', 'Baixa'),
            ('MEDIA', 'Média'),
            ('ALTA', 'Alta'),
            ('URGENTE', 'Urgente'),
        ],
        default='MEDIA'
    )
    
    observacoes = models.TextField('Observações', blank=True)
    
    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.nome} ({self.get_status_display()})"
    
    @property
    def percentual_gasto(self):
        """Percentual do orçamento já gasto"""
        if self.orcamento_previsto > 0:
            return (self.custo_realizado / self.orcamento_previsto) * 100
        return 0
    
    @property
    def saldo_orcamento(self):
        """Saldo restante do orçamento"""
        return self.orcamento_previsto - self.custo_realizado
    
    @property
    def dias_restantes(self):
        """Dias até a conclusão prevista"""
        from datetime import date
        if self.data_conclusao_real:
            return 0
        delta = self.data_conclusao_prevista - date.today()
        return max(delta.days, 0)


class EtapaProjeto(models.Model):
    """Etapas de um projeto"""
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='etapas')
    
    nome = models.CharField('Nome da Etapa', max_length=150)
    descricao = models.TextField('Descrição', blank=True)
    ordem = models.IntegerField('Ordem', default=1)
    
    data_inicio = models.DateField('Data de Início', null=True, blank=True)
    data_conclusao = models.DateField('Data de Conclusão', null=True, blank=True)
    
    concluida = models.BooleanField('Concluída', default=False)
    percentual_conclusao = models.IntegerField('% de Conclusão', default=0)
    
    custo_previsto = models.DecimalField('Custo Previsto', max_digits=10, decimal_places=2, default=0)
    custo_realizado = models.DecimalField('Custo Realizado', max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = 'Etapa do Projeto'
        verbose_name_plural = 'Etapas do Projeto'
        ordering = ['projeto', 'ordem']
    
    def __str__(self):
        return f"{self.projeto.nome} - {self.nome}"

