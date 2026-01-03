# -*- coding: utf-8 -*-
"""
Views administrativas para operações de manutenção
"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


def is_superuser(user):
    """Verifica se o usuário é superusuário"""
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["POST"])
def limpar_usuarios_admin(request):
    """
    View administrativa para limpar usuários (exceto admin)
    Apenas superusuários podem executar
    """
    try:
        senha_admin = 'L6171r12@@'
        username_admin = 'admin'
        
        with transaction.atomic():
            # Obter ou criar admin
            admin, created = User.objects.get_or_create(
                username=username_admin,
                defaults={
                    'email': 'admin@monpec.com.br',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            
            if not created:
                # Atualizar admin existente
                admin.is_staff = True
                admin.is_superuser = True
                admin.is_active = True
                admin.email = 'admin@monpec.com.br'
                admin.save()
            
            # Definir senha do admin
            admin.set_password(senha_admin)
            admin.save()
            
            # Excluir todos os outros usuários
            usuarios_excluidos = User.objects.exclude(username=username_admin).delete()
            
            logger.info(f'Limpeza de usuários executada: {usuarios_excluidos[0]} usuário(s) excluído(s)')
        
        return JsonResponse({
            'success': True,
            'message': f'Usuários limpos com sucesso! {usuarios_excluidos[0]} usuário(s) excluído(s). Apenas o admin foi mantido.'
        })
    except Exception as e:
        logger.error(f'Erro ao limpar usuários: {e}', exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Erro ao limpar usuários: {str(e)}'
        }, status=500)

