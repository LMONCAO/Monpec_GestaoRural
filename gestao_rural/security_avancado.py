"""
Módulo de segurança avançada para o sistema MONPEC
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from .models_auditoria import LogAuditoria, VerificacaoEmail, SessaoSegura


def obter_ip_address(request) -> str:
    """Obtém o endereço IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def registrar_log_auditoria(
    tipo_acao: str,
    descricao: str,
    usuario: Optional[User] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    nivel_severidade: str = LogAuditoria.NivelSeveridade.MEDIO,
    sucesso: bool = True,
    erro: Optional[str] = None,
    metadata: Optional[dict] = None,
):
    """Registra um log de auditoria"""
    try:
        LogAuditoria.objects.create(
            usuario=usuario,
            tipo_acao=tipo_acao,
            descricao=descricao,
            ip_address=ip_address,
            user_agent=user_agent or '',
            nivel_severidade=nivel_severidade,
            sucesso=sucesso,
            erro=erro or '',
            metadata=metadata or {},
        )
    except Exception as e:
        # Não falhar se não conseguir registrar log
        import logging
        logging.error(f"Erro ao registrar log de auditoria: {e}")


def gerar_token_verificacao_email() -> str:
    """Gera um token seguro para verificação de e-mail"""
    return secrets.token_urlsafe(32)


def criar_verificacao_email(usuario: User) -> VerificacaoEmail:
    """Cria registro de verificação de e-mail para novo usuário"""
    token = gerar_token_verificacao_email()
    token_expira_em = timezone.now() + timedelta(days=7)  # 7 dias para verificar
    
    verificacao, _ = VerificacaoEmail.objects.update_or_create(
        usuario=usuario,
        defaults={
            'token': token,
            'token_expira_em': token_expira_em,
            'email_verificado': False,
            'tentativas_verificacao': 0,
        }
    )
    
    return verificacao


def enviar_email_verificacao(usuario: User, verificacao: VerificacaoEmail) -> bool:
    """Envia e-mail de verificação para o usuário"""
    try:
        link_verificacao = f"{settings.SITE_URL}/verificar-email/{verificacao.token}/"
        
        assunto = "Verifique seu e-mail - MONPEC"
        mensagem = f"""
Olá {usuario.get_full_name() or usuario.username},

Bem-vindo ao sistema MONPEC!

Para ativar sua conta, por favor verifique seu e-mail clicando no link abaixo:

{link_verificacao}

Este link expira em 7 dias.

Se você não criou esta conta, pode ignorar este e-mail.

Atenciosamente,
Equipe MONPEC
"""
        
        send_mail(
            assunto,
            mensagem,
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            fail_silently=False,
        )
        
        registrar_log_auditoria(
            tipo_acao=LogAuditoria.TipoAcao.CRIAR_USUARIO,
            descricao=f"E-mail de verificação enviado para {usuario.email}",
            usuario=usuario,
            nivel_severidade=LogAuditoria.NivelSeveridade.BAIXO,
        )
        
        return True
    except Exception as e:
        registrar_log_auditoria(
            tipo_acao=LogAuditoria.TipoAcao.CRIAR_USUARIO,
            descricao=f"Erro ao enviar e-mail de verificação: {e}",
            usuario=usuario,
            nivel_severidade=LogAuditoria.NivelSeveridade.ALTO,
            sucesso=False,
            erro=str(e),
        )
        return False


def verificar_email_token(token: str) -> Tuple[bool, Optional[User], str]:
    """
    Verifica token de e-mail
    Retorna: (sucesso, usuario, mensagem)
    """
    try:
        verificacao = VerificacaoEmail.objects.get(token=token)
    except VerificacaoEmail.DoesNotExist:
        return False, None, "Token inválido."
    
    if verificacao.email_verificado:
        return False, None, "E-mail já foi verificado."
    
    if timezone.now() > verificacao.token_expira_em:
        return False, None, "Token expirado. Solicite um novo link de verificação."
    
    if verificacao.tentativas_verificacao >= 5:
        return False, None, "Muitas tentativas de verificação. Entre em contato com o suporte."
    
    # Verificar e-mail
    verificacao.email_verificado = True
    verificacao.verificado_em = timezone.now()
    verificacao.tentativas_verificacao += 1
    verificacao.save()
    
    # Ativar usuário
    usuario = verificacao.usuario
    usuario.is_active = True
    usuario.save()
    
    registrar_log_auditoria(
        tipo_acao=LogAuditoria.TipoAcao.CRIAR_USUARIO,
        descricao=f"E-mail verificado com sucesso: {usuario.email}",
        usuario=usuario,
        nivel_severidade=LogAuditoria.NivelSeveridade.BAIXO,
    )
    
    return True, usuario, "E-mail verificado com sucesso!"


def registrar_sessao_segura(usuario: User, session_key: str, ip_address: str, user_agent: str = ''):
    """Registra sessão segura do usuário"""
    SessaoSegura.objects.update_or_create(
        session_key=session_key,
        defaults={
            'usuario': usuario,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'ativo': True,
        }
    )


def verificar_sessao_segura(usuario: User, session_key: str, ip_address: str) -> bool:
    """Verifica se a sessão é segura e válida"""
    try:
        sessao = SessaoSegura.objects.get(
            usuario=usuario,
            session_key=session_key,
            ativo=True
        )
        
        # Verificar se IP mudou (possível roubo de sessão)
        if sessao.ip_address != ip_address:
            registrar_log_auditoria(
                tipo_acao=LogAuditoria.TipoAcao.ACESSO_NAO_AUTORIZADO,
                descricao=f"Mudança de IP detectada: {sessao.ip_address} -> {ip_address}",
                usuario=usuario,
                ip_address=ip_address,
                nivel_severidade=LogAuditoria.NivelSeveridade.ALTO,
                sucesso=False,
            )
            # Invalidar sessão antiga
            sessao.ativo = False
            sessao.save(update_fields=['ativo'])
            return False
        
        # Atualizar última atividade
        sessao.ultima_atividade = timezone.now()
        sessao.save(update_fields=['ultima_atividade'])
        
        return True
    except SessaoSegura.DoesNotExist:
        # Sessão não existe ainda - será criada pelo middleware
        return True  # Permite criar na primeira vez


def invalidar_sessao_segura(session_key: str):
    """Invalida uma sessão segura"""
    SessaoSegura.objects.filter(session_key=session_key).update(ativo=False)


def verificar_assinatura_ativa_para_pagamento(usuario: User) -> Tuple[bool, str]:
    """
    Verifica se o usuário pode processar pagamento
    Retorna: (pode_processar, mensagem)
    """
    from .models import AssinaturaCliente
    
    try:
        assinatura = AssinaturaCliente.objects.get(usuario=usuario)
        
        # Verificar se já tem assinatura ativa
        if assinatura.status == AssinaturaCliente.Status.ATIVA:
            return False, "Você já possui uma assinatura ativa."
        
        # Verificar se tem assinatura pendente recente
        if assinatura.status == AssinaturaCliente.Status.PENDENTE:
            # Verificar se foi criada há menos de 1 hora
            tempo_decorrido = timezone.now() - assinatura.criado_em
            if tempo_decorrido < timedelta(hours=1):
                return False, "Você já tem um pagamento pendente. Aguarde a confirmação."
        
        return True, "OK"
        
    except AssinaturaCliente.DoesNotExist:
        return True, "OK"


def validar_criacao_usuario_segura(
    criado_por: User,
    email: str,
    assinatura_id: int,
    ip_address: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Valida criação de usuário com verificações de segurança
    Retorna: (pode_criar, mensagem)
    """
    from .models import AssinaturaCliente, TenantUsuario
    from .services.tenant_access import obter_assinatura_do_usuario
    
    # 1. Verificar se quem está criando tem permissão
    assinatura_criador = obter_assinatura_do_usuario(criado_por)
    if not assinatura_criador:
        return False, "Você não possui uma assinatura ativa."
    
    if assinatura_criador.status != AssinaturaCliente.Status.ATIVA:
        return False, "Sua assinatura não está ativa."
    
    # 2. Verificar se a assinatura é a mesma
    try:
        assinatura = AssinaturaCliente.objects.get(id=assinatura_id)
        if assinatura != assinatura_criador:
            registrar_log_auditoria(
                tipo_acao=LogAuditoria.TipoAcao.ACESSO_NAO_AUTORIZADO,
                descricao=f"Tentativa de criar usuário em assinatura diferente: {assinatura_id}",
                usuario=criado_por,
                ip_address=ip_address,
                nivel_severidade=LogAuditoria.NivelSeveridade.CRITICO,
                sucesso=False,
            )
            return False, "Você não tem permissão para criar usuários nesta assinatura."
    except AssinaturaCliente.DoesNotExist:
        return False, "Assinatura não encontrada."
    
    # 3. Verificar se e-mail já está em uso
    if User.objects.filter(email__iexact=email).exists():
        usuario_existente = User.objects.get(email__iexact=email)
        if hasattr(usuario_existente, 'tenant_profile'):
            if usuario_existente.tenant_profile.assinatura != assinatura:
                return False, "Este e-mail já está vinculado a outra conta."
    
    # 4. Rate limiting: máximo 3 usuários por hora
    cache_key = f"criar_usuario_rate_limit_{criado_por.id}"
    tentativas = cache.get(cache_key, 0)
    if tentativas >= 3:
        registrar_log_auditoria(
            tipo_acao=LogAuditoria.TipoAcao.ACESSO_NAO_AUTORIZADO,
            descricao="Rate limit excedido para criação de usuários",
            usuario=criado_por,
            ip_address=ip_address,
            nivel_severidade=LogAuditoria.NivelSeveridade.ALTO,
            sucesso=False,
        )
        return False, "Muitas tentativas de criar usuários. Aguarde 1 hora."
    
    cache.set(cache_key, tentativas + 1, 3600)  # 1 hora
    
    return True, "OK"

