"""
Decorators e funções auxiliares para verificação de permissões e segurança.
"""
from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
import logging

from .models import Propriedade

logger = logging.getLogger(__name__)


def usuario_tem_acesso_propriedade(usuario, propriedade):
    """
    Verifica se o usuário tem acesso à propriedade.
    
    Args:
        usuario: Usuário a verificar
        propriedade: Propriedade a verificar
        
    Returns:
        True se o usuário tem acesso, False caso contrário
    """
    if usuario.is_superuser:
        return True
    
    if not propriedade.produtor:
        return False
    
    return propriedade.produtor.usuario_responsavel == usuario


def obter_propriedade_com_permissao(usuario, propriedade_id):
    """
    Obtém uma propriedade verificando se o usuário tem permissão de acesso.
    
    Args:
        usuario: Usuário logado
        propriedade_id: ID da propriedade
        
    Returns:
        Propriedade se o usuário tem acesso
        
    Raises:
        Http404: Se a propriedade não existir ou usuário não tiver acesso
    """
    propriedade = get_object_or_404(
        Propriedade.objects.select_related('produtor'),
        id=propriedade_id
    )
    
    if not usuario_tem_acesso_propriedade(usuario, propriedade):
        logger.warning(
            f'Usuário {usuario.username} tentou acessar propriedade {propriedade_id} sem permissão'
        )
        raise Http404("Propriedade não encontrada ou você não tem permissão para acessá-la.")
    
    return propriedade


def verificar_propriedade_usuario(view_func):
    """
    Decorator que verifica se o usuário tem acesso à propriedade antes de executar a view.
    
    Uso:
        @login_required
        @verificar_propriedade_usuario
        def minha_view(request, propriedade_id, ...):
            propriedade = request.propriedade  # Já validada e disponível
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, propriedade_id, *args, **kwargs):
        try:
            propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
            # Adiciona propriedade ao request para uso na view
            request.propriedade = propriedade
            return view_func(request, propriedade_id, *args, **kwargs)
        except Http404:
            # Re-raise para manter comportamento padrão do Django
            raise
        except Exception as e:
            logger.error(f'Erro ao verificar permissão de propriedade: {e}', exc_info=True)
            raise Http404("Erro ao verificar permissões.")
    
    return wrapper


def verificar_propriedade_usuario_json(view_func):
    """
    Decorator similar ao verificar_propriedade_usuario, mas retorna JSON para APIs.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, propriedade_id, *args, **kwargs):
        try:
            propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
            request.propriedade = propriedade
            return view_func(request, propriedade_id, *args, **kwargs)
        except Http404:
            return JsonResponse({
                'success': False,
                'error': 'Propriedade não encontrada ou você não tem permissão para acessá-la.'
            }, status=404)
        except Exception as e:
            logger.error(f'Erro ao verificar permissão de propriedade (API): {e}', exc_info=True)
            return JsonResponse({
                'success': False,
                'error': 'Erro ao verificar permissões.'
            }, status=500)
    
    return wrapper


