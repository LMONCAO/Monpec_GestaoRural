# -*- coding: utf-8 -*-
"""
Views customizadas para recuperação de senha
Bloqueia usuários demo de redefinir senha
"""

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class CustomPasswordResetView(PasswordResetView):
    """View customizada para bloquear recuperação de senha de usuários demo"""
    
    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', '').strip().lower()
        
        # Verificar se é usuário demo
        from django.contrib.auth.models import User
        from .models_auditoria import UsuarioAtivo
        
        try:
            user = User.objects.filter(email=email).first()
            if user:
                # Verificar se é usuário demo padrão
                if user.username in ['demo', 'demo_monpec']:
                    logger.warning(f'Tentativa de recuperação de senha bloqueada para usuário demo: {user.username}')
                    messages.warning(
                        request,
                        '⚠️ <strong>Versão de Demonstração:</strong> A recuperação de senha não está disponível para usuários demo. '
                        'Para ter acesso completo ao sistema, adquira uma assinatura.'
                    )
                    return redirect('assinaturas_dashboard')
                
                # Verificar se é usuário de demonstração (do popup)
                try:
                    UsuarioAtivo.objects.get(usuario=user)
                    logger.warning(f'Tentativa de recuperação de senha bloqueada para usuário de demonstração: {user.username}')
                    messages.warning(
                        request,
                        '⚠️ <strong>Versão de Demonstração:</strong> A recuperação de senha não está disponível para usuários de demonstração. '
                        'Para ter acesso completo ao sistema, adquira uma assinatura.'
                    )
                    return redirect('assinaturas_dashboard')
                except UsuarioAtivo.DoesNotExist:
                    pass
        except Exception as e:
            logger.error(f'Erro ao verificar usuário demo na recuperação de senha: {e}')
        
        # Se não for demo, continuar com o processo normal
        return super().post(request, *args, **kwargs)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """View customizada para bloquear confirmação de senha de usuários demo"""
    
    def dispatch(self, *args, **kwargs):
        # Verificar se o usuário é demo antes de permitir a redefinição
        try:
            from django.contrib.auth.models import User
            from .models_auditoria import UsuarioAtivo
            
            # Obter o usuário do token
            uidb64 = kwargs.get('uidb64')
            if uidb64:
                from django.utils.http import urlsafe_base64_decode
                from django.contrib.auth.tokens import default_token_generator
                
                try:
                    uid = urlsafe_base64_decode(uidb64).decode()
                    user = User.objects.get(pk=uid)
                    
                    # Verificar se é usuário demo padrão
                    if user.username in ['demo', 'demo_monpec']:
                        logger.warning(f'Tentativa de confirmação de recuperação de senha bloqueada para usuário demo: {user.username}')
                        messages.warning(
                            self.request,
                            '⚠️ <strong>Versão de Demonstração:</strong> A recuperação de senha não está disponível para usuários demo. '
                            'Para ter acesso completo ao sistema, adquira uma assinatura.'
                        )
                        return redirect('assinaturas_dashboard')
                    
                    # Verificar se é usuário de demonstração (do popup)
                    try:
                        UsuarioAtivo.objects.get(usuario=user)
                        logger.warning(f'Tentativa de confirmação de recuperação de senha bloqueada para usuário de demonstração: {user.username}')
                        messages.warning(
                            self.request,
                            '⚠️ <strong>Versão de Demonstração:</strong> A recuperação de senha não está disponível para usuários de demonstração. '
                            'Para ter acesso completo ao sistema, adquira uma assinatura.'
                        )
                        return redirect('assinaturas_dashboard')
                    except UsuarioAtivo.DoesNotExist:
                        pass
                except (ValueError, User.DoesNotExist):
                    pass
        except Exception as e:
            logger.error(f'Erro ao verificar usuário demo na confirmação de recuperação de senha: {e}')
        
        return super().dispatch(*args, **kwargs)




















