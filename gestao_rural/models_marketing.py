"""
Modelos para o módulo de Marketing - Geração de Posts e Captura de Leads
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class TemplatePost(models.Model):
    """Template para geração automática de posts"""
    
    TIPO_POST_CHOICES = [
        ('apresentacao', 'Apresentação'),
        ('problema_solucao', 'Problema x Solução'),
        ('funcionalidade', 'Funcionalidade'),
        ('prova_social', 'Prova Social'),
        ('educacao', 'Educação/Dica'),
        ('vendas', 'Vendas/Oferta'),
        ('engajamento', 'Engajamento'),
        ('humanizacao', 'Humanização'),
        ('tendencias', 'Tendências'),
    ]
    
    REDE_SOCIAL_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('linkedin', 'LinkedIn'),
        ('whatsapp', 'WhatsApp'),
        ('geral', 'Geral (Todas)'),
    ]
    
    nome = models.CharField(max_length=200, help_text="Nome identificador do template")
    tipo_post = models.CharField(max_length=50, choices=TIPO_POST_CHOICES)
    rede_social = models.CharField(max_length=50, choices=REDE_SOCIAL_CHOICES, default='geral')
    
    # Template com variáveis que podem ser substituídas
    # Use {nome_produto}, {beneficio_1}, {beneficio_2}, {cta}, etc.
    conteudo = models.TextField(help_text="Conteúdo do post com variáveis entre chaves {variavel}")
    
    # Hashtags sugeridas
    hashtags = models.TextField(blank=True, help_text="Hashtags separadas por vírgula")
    
    # Variáveis disponíveis (JSON)
    variaveis_disponiveis = models.JSONField(
        default=dict,
        blank=True,
        help_text="Variáveis que podem ser usadas no template (JSON)"
    )
    
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Template de Post"
        verbose_name_plural = "Templates de Posts"
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_post_display()})"


class PostGerado(models.Model):
    """Posts gerados automaticamente a partir dos templates"""
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('aprovado', 'Aprovado'),
        ('publicado', 'Publicado'),
        ('arquivado', 'Arquivado'),
    ]
    
    template = models.ForeignKey(TemplatePost, on_delete=models.SET_NULL, null=True, blank=True)
    titulo = models.CharField(max_length=200)
    conteudo_final = models.TextField(help_text="Conteúdo do post já processado (sem variáveis)")
    hashtags_final = models.CharField(max_length=500, blank=True)
    
    rede_social = models.CharField(max_length=50, choices=TemplatePost.REDE_SOCIAL_CHOICES)
    tipo_post = models.CharField(max_length=50, choices=TemplatePost.TIPO_POST_CHOICES)
    
    # Variáveis usadas na geração (JSON)
    variaveis_usadas = models.JSONField(default=dict, blank=True)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='rascunho')
    
    # Agendamento
    agendar_para = models.DateTimeField(null=True, blank=True, help_text="Agendar publicação para data/hora específica")
    publicado_em = models.DateTimeField(null=True, blank=True)
    
    # Métricas
    visualizacoes = models.IntegerField(default=0)
    engajamento = models.IntegerField(default=0)
    
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Post Gerado"
        verbose_name_plural = "Posts Gerados"
    
    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"


class LeadInteressado(models.Model):
    """Leads capturados através da landing page de acesso gratuito"""
    
    STATUS_CHOICES = [
        ('novo', 'Novo'),
        ('contatado', 'Contatado'),
        ('qualificado', 'Qualificado'),
        ('convertido', 'Convertido'),
        ('descartado', 'Descartado'),
    ]
    
    # Dados básicos
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    
    # Informações adicionais
    propriedade_nome = models.CharField(max_length=200, blank=True, help_text="Nome da propriedade/fazenda")
    tipo_atividade = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('pecuaria_corte', 'Pecuária de Corte'),
            ('pecuaria_leite', 'Pecuária de Leite'),
            ('agricultura', 'Agricultura'),
            ('outro', 'Outro'),
        ]
    )
    
    # Status e rastreamento
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='novo')
    origem = models.CharField(max_length=100, default='landing_page', help_text="De onde veio o lead")
    
    # Acesso gratuito
    credenciais_enviadas = models.BooleanField(default=False)
    credenciais_enviadas_em = models.DateTimeField(null=True, blank=True)
    
    # Notas internas
    observacoes = models.TextField(blank=True)
    
    # Metadados
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Lead Interessado"
        verbose_name_plural = "Leads Interessados"
    
    def __str__(self):
        return f"{self.nome} ({self.email}) - {self.get_status_display()}"


class CampanhaMarketing(models.Model):
    """Campanhas de marketing para organizar posts e leads"""
    
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    
    # Período
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    
    # Objetivos
    objetivo_principal = models.TextField(help_text="Qual o objetivo principal desta campanha?")
    publico_alvo = models.TextField(help_text="Descrição do público-alvo")
    
    # Métricas
    meta_leads = models.IntegerField(default=0)
    meta_conversoes = models.IntegerField(default=0)
    
    ativa = models.BooleanField(default=True)
    
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = "Campanha de Marketing"
        verbose_name_plural = "Campanhas de Marketing"
    
    def __str__(self):
        return self.nome
    
    def leads_associados(self):
        """Retorna número de leads associados a esta campanha"""
        return self.leads_campanha.count()
    
    def posts_associados(self):
        """Retorna número de posts associados a esta campanha"""
        return self.posts_campanha.count()


class ConfiguracaoMarketing(models.Model):
    """Configurações globais do módulo de marketing"""
    
    # URLs e links
    url_site = models.URLField(default='https://monpec.com.br', help_text="URL principal do site")
    url_whatsapp = models.CharField(
        max_length=50,
        default='',
        help_text="Número do WhatsApp (formato: 5511999999999)"
    )
    email_contato = models.EmailField(default='contato@monpec.com.br')
    
    # Mensagens padrão
    mensagem_cta_padrao = models.TextField(
        default="👉 Entre em contato e descubra como o MONPEC pode transformar sua gestão!",
        help_text="Call-to-action padrão para posts"
    )
    
    # Variáveis padrão para templates
    variaveis_padrao = models.JSONField(
        default=dict,
        help_text="Variáveis padrão usadas na geração de posts (JSON)"
    )
    
    # Configurações de acesso gratuito
    ativar_acesso_gratuito = models.BooleanField(
        default=True,
        help_text="Ativar oferta de acesso gratuito na landing page"
    )
    mensagem_acesso_gratuito = models.TextField(
        default="Acesse gratuitamente o MONPEC e descubra como transformar sua gestão rural!",
        help_text="Mensagem de acesso gratuito"
    )
    
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Marketing"
        verbose_name_plural = "Configurações de Marketing"
    
    def __str__(self):
        return "Configurações de Marketing"
    
    def save(self, *args, **kwargs):
        # Garantir que só existe uma instância
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração única, criando se não existir"""
        config, created = cls.objects.get_or_create(pk=1)
        return config




























