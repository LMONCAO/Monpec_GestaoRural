"""
Views para funcionalidades de segurança
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from .security_avancado import (
    verificar_email_token,
    registrar_log_auditoria,
    obter_ip_address,
)
from .models_auditoria import VerificacaoEmail


def verificar_email(request, token):
    """View para verificar e-mail do usuário"""
    sucesso, usuario, mensagem = verificar_email_token(token)
    
    if sucesso:
        messages.success(request, mensagem)
        return redirect('login')
    else:
        messages.error(request, mensagem)
        return redirect('login')


@login_required
def reenviar_email_verificacao(request):
    """Reenvia e-mail de verificação"""
    from .security_avancado import criar_verificacao_email, enviar_email_verificacao
    
    try:
        verificacao = VerificacaoEmail.objects.get(usuario=request.user)
        if verificacao.email_verificado:
            messages.info(request, "Seu e-mail já foi verificado.")
            return redirect('dashboard')
        
        # Criar novo token
        verificacao = criar_verificacao_email(request.user)
        enviar_email_verificacao(request.user, verificacao)
        
        messages.success(request, "E-mail de verificação reenviado. Verifique sua caixa de entrada.")
        
        registrar_log_auditoria(
            tipo_acao='RECUPERAR_SENHA',
            descricao="E-mail de verificação reenviado",
            usuario=request.user,
            ip_address=obter_ip_address(request),
            nivel_severidade='BAIXO',
        )
        
    except VerificacaoEmail.DoesNotExist:
        messages.info(request, "Não há verificação de e-mail pendente.")
    
    return redirect('dashboard')


@login_required
def logs_auditoria(request):
    """Visualizar logs de auditoria do próprio usuário"""
    from .models_auditoria import LogAuditoria
    from django.core.paginator import Paginator
    
    # Apenas admin pode ver todos os logs
    if not request.user.is_superuser:
        logs = LogAuditoria.objects.filter(usuario=request.user)
    else:
        logs = LogAuditoria.objects.all()
    
    logs = logs.order_by('-criado_em')[:100]  # Últimos 100
    
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'logs': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'gestao_rural/logs_auditoria.html', context)


@login_required
def informacoes_seguranca(request):
    """Página com informações sobre segurança do sistema"""
    from django.contrib.auth.models import User
    from .security import verificar_usuarios_inseguros, USUARIOS_PADRAO_PERIGOSOS
    
    # Verificar problemas de segurança
    problemas = verificar_usuarios_inseguros()
    superusuarios = User.objects.filter(is_superuser=True)
    usuarios_sem_senha = [u for u in User.objects.all() if not u.has_usable_password() and u.is_active]
    usuarios_padrao = User.objects.filter(username__in=USUARIOS_PADRAO_PERIGOSOS, is_active=True)
    
    context = {
        'problemas': problemas,
        'total_problemas': len(problemas),
        'superusuarios': superusuarios,
        'total_superusuarios': superusuarios.count(),
        'usuarios_sem_senha': usuarios_sem_senha,
        'total_usuarios_sem_senha': len(usuarios_sem_senha),
        'usuarios_padrao': usuarios_padrao,
        'total_usuarios_padrao': usuarios_padrao.count(),
        'usuarios_padrao_lista': USUARIOS_PADRAO_PERIGOSOS,
    }
    
    return render(request, 'gestao_rural/seguranca_info.html', context)
