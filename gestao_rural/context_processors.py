"""
Context processors para templates
"""
from django.conf import settings


def demo_mode(request):
    """
    Adiciona DEMO_MODE ao contexto de todos os templates
    """
    return {
        'DEMO_MODE': getattr(settings, 'DEMO_MODE', False),
        'DEMO_LINK_PAGAMENTO': getattr(settings, 'DEMO_LINK_PAGAMENTO', '/assinaturas/'),
        'google_analytics_id': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
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
        }
    
    # Superusuários e staff sempre têm acesso
    if request.user.is_superuser or request.user.is_staff:
        return {
            'acesso_liberado': True,
            'assinatura': None,
        }
    
    # Verificar se o middleware já adicionou as informações
    if hasattr(request, 'acesso_liberado') and hasattr(request, 'assinatura'):
        return {
            'acesso_liberado': request.acesso_liberado,
            'assinatura': request.assinatura,
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
    
    return {
        'acesso_liberado': acesso_liberado,
        'assinatura': assinatura,
    }





