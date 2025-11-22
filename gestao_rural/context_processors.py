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





