"""
Modelos para auditoria e logs de segurança
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class LogAuditoria(models.Model):
    """Log de todas as ações sensíveis do sistema"""
    
    class TipoAcao(models.TextChoices):
        LOGIN = 'LOGIN', 'Login'
        LOGOUT = 'LOGOUT', 'Logout'
        LOGIN_FALHA = 'LOGIN_FALHA', 'Tentativa de Login Falha'
        CRIAR_USUARIO = 'CRIAR_USUARIO', 'Criar Usuário'
        EDITAR_USUARIO = 'EDITAR_USUARIO', 'Editar Usuário'
        DESATIVAR_USUARIO = 'DESATIVAR_USUARIO', 'Desativar Usuário'
        REATIVAR_USUARIO = 'REATIVAR_USUARIO', 'Reativar Usuário'
        ALTERAR_SENHA = 'ALTERAR_SENHA', 'Alterar Senha'
        RECUPERAR_SENHA = 'RECUPERAR_SENHA', 'Recuperar Senha'
        CRIAR_ASSINATURA = 'CRIAR_ASSINATURA', 'Criar Assinatura'
        ATUALIZAR_ASSINATURA = 'ATUALIZAR_ASSINATURA', 'Atualizar Assinatura'
        CANCELAR_ASSINATURA = 'CANCELAR_ASSINATURA', 'Cancelar Assinatura'
        PROCESSAR_PAGAMENTO = 'PROCESSAR_PAGAMENTO', 'Processar Pagamento'
        WEBHOOK_STRIPE = 'WEBHOOK_STRIPE', 'Webhook Stripe'
        ACESSO_NAO_AUTORIZADO = 'ACESSO_NAO_AUTORIZADO', 'Tentativa de Acesso Não Autorizado'
        ALTERAR_PERMISSOES = 'ALTERAR_PERMISSOES', 'Alterar Permissões'
    
    class NivelSeveridade(models.TextChoices):
        BAIXO = 'BAIXO', 'Baixo'
        MEDIO = 'MEDIO', 'Médio'
        ALTO = 'ALTO', 'Alto'
        CRITICO = 'CRITICO', 'Crítico'
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_auditoria',
        verbose_name="Usuário"
    )
    tipo_acao = models.CharField(
        max_length=50,
        choices=TipoAcao.choices,
        verbose_name="Tipo de Ação"
    )
    nivel_severidade = models.CharField(
        max_length=20,
        choices=NivelSeveridade.choices,
        default=NivelSeveridade.MEDIO,
        verbose_name="Nível de Severidade"
    )
    descricao = models.TextField(verbose_name="Descrição")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Endereço IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadados")
    sucesso = models.BooleanField(default=True, verbose_name="Sucesso")
    erro = models.TextField(blank=True, verbose_name="Erro (se houver)")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['usuario', '-criado_em']),
            models.Index(fields=['tipo_acao', '-criado_em']),
            models.Index(fields=['ip_address', '-criado_em']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_acao_display()} - {self.usuario or 'Sistema'} - {self.criado_em}"


class VerificacaoEmail(models.Model):
    """Verificação de e-mail para novos usuários"""
    
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='verificacao_email',
        verbose_name="Usuário"
    )
    token = models.CharField(max_length=64, unique=True, verbose_name="Token")
    email_verificado = models.BooleanField(default=False, verbose_name="E-mail Verificado")
    token_expira_em = models.DateTimeField(verbose_name="Token Expira em")
    tentativas_verificacao = models.PositiveIntegerField(default=0, verbose_name="Tentativas")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    verificado_em = models.DateTimeField(null=True, blank=True, verbose_name="Verificado em")
    
    class Meta:
        verbose_name = "Verificação de E-mail"
        verbose_name_plural = "Verificações de E-mail"
    
    def __str__(self):
        status = "Verificado" if self.email_verificado else "Pendente"
        return f"{self.usuario.username} - {status}"


class SessaoSegura(models.Model):
    """Rastreamento de sessões ativas para segurança"""
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessoes_seguras',
        verbose_name="Usuário"
    )
    session_key = models.CharField(max_length=40, unique=True, verbose_name="Chave da Sessão")
    ip_address = models.GenericIPAddressField(verbose_name="Endereço IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    ultima_atividade = models.DateTimeField(auto_now=True, verbose_name="Última Atividade")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Sessão Segura"
        verbose_name_plural = "Sessões Seguras"
        ordering = ['-ultima_atividade']
        indexes = [
            models.Index(fields=['usuario', '-ultima_atividade']),
            models.Index(fields=['ip_address', '-ultima_atividade']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.ip_address} - {self.ultima_atividade}"


class UsuarioAtivo(models.Model):
    """Usuários ativos do sistema de demonstração"""
    
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='usuario_ativo',
        verbose_name="Usuário"
    )
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    email = models.EmailField(verbose_name="E-mail")
    telefone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    primeiro_acesso = models.DateTimeField(auto_now_add=True, verbose_name="Primeiro Acesso")
    ultimo_acesso = models.DateTimeField(auto_now=True, verbose_name="Último Acesso")
    total_acessos = models.PositiveIntegerField(default=0, verbose_name="Total de Acessos")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Usuário Ativo"
        verbose_name_plural = "Usuários Ativos"
        ordering = ['-ultimo_acesso']
    
    def __str__(self):
        return f"{self.nome_completo} ({self.usuario.username})"

