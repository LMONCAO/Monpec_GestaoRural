"""
Context processors para templates
"""
from django.conf import settings


def _is_usuario_demo(user):
    """
    Função helper centralizada para verificar se um usuário é demo.
    Retorna True se:
    - username está em ['demo', 'demo_monpec']
    - ou tem registro UsuarioAtivo (criado pelo botão demonstração)
    """
    if not user or not user.is_authenticated:
        return False
    
    # Verificar se é usuário demo padrão
    if user.username in ['demo', 'demo_monpec']:
        return True
    
    # Verificar se tem UsuarioAtivo (usuário criado pelo popup)
    try:
        from .models_auditoria import UsuarioAtivo
        UsuarioAtivo.objects.get(usuario=user)
        return True
    except:
        return False


def demo_mode(request):
    """
    Adiciona DEMO_MODE ao contexto de todos os templates
    """
    is_demo_user = _is_usuario_demo(request.user)
    
    return {
        'DEMO_MODE': getattr(settings, 'DEMO_MODE', False),
        'DEMO_LINK_PAGAMENTO': getattr(settings, 'DEMO_LINK_PAGAMENTO', '/assinaturas/'),
        'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'IS_DEMO_USER': is_demo_user,  # Indica se o usuário atual é demo
    }


def assinatura_info(request):
    """
    Adiciona informações de assinatura ao contexto de todos os templates.
    Usado para mostrar o botão "Garanta sua assinatura agora" quando necessário.
    """
    if not request.user.is_authenticated:
        return {
            'acesso_liberado': True,  # Usuários não autenticados não precisam de verificação
            'assinatura': None,
            'IS_DEMO_USER': False,
            'IS_ASSINANTE': False,  # Usuários não autenticados não são assinantes
        }
    
    # Superusuários e staff sempre têm acesso
    if request.user.is_superuser or request.user.is_staff:
        return {
            'acesso_liberado': True,
            'assinatura': None,
            'IS_DEMO_USER': False,
            'IS_ASSINANTE': True,  # Superusuários são tratados como assinantes
        }
    
    # Verificar se é usuário demo PRIMEIRO (usuários criados pelo botão demonstração ou demo padrão)
    is_demo_user = _is_usuario_demo(request.user)
    
    # Se for usuário demo, sempre ter acesso_liberado = False (versão pré-lançamento)
    if is_demo_user:
        request.IS_DEMO_USER = is_demo_user  # Adiciona ao request para uso em outros middlewares/views
        return {
            'acesso_liberado': False,  # Usuários demo têm acesso restrito (pré-lançamento)
            'assinatura': None,
            'IS_DEMO_USER': True,
            'IS_ASSINANTE': False,  # Demo nunca é assinante
        }
    
    # Verificar se o middleware já adicionou as informações
    if hasattr(request, 'acesso_liberado') and hasattr(request, 'assinatura'):
        is_assinante_middleware = not is_demo_user and request.acesso_liberado
        return {
            'acesso_liberado': request.acesso_liberado,
            'assinatura': request.assinatura,
            'IS_DEMO_USER': False,
            'IS_ASSINANTE': is_assinante_middleware,
        }
    
    # Se o middleware não executou, buscar diretamente
    try:
        from .models import AssinaturaCliente
        assinatura = AssinaturaCliente.objects.select_related('plano').filter(usuario=request.user).first()
        if assinatura:
            acesso_liberado = assinatura.acesso_liberado
        else:
            acesso_liberado = False
            assinatura = None
    except Exception:
        acesso_liberado = True  # Em caso de erro, permitir acesso
        assinatura = None
    
    # Verificar se é assinante (não demo e com acesso liberado)
    is_assinante = not is_demo_user and acesso_liberado
    
    return {
        'acesso_liberado': acesso_liberado,
        'assinatura': assinatura,
        'IS_DEMO_USER': False,
        'IS_ASSINANTE': is_assinante,  # True apenas para assinantes (não demo)
    }





