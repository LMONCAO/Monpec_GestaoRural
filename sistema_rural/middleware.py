"""
Middleware customizado para permitir hosts do Cloud Run dinamicamente.
"""
from django.conf import settings


class CloudRunHostMiddleware:
    """
    Middleware para permitir hosts do Cloud Run dinamicamente.
    Cloud Run URLs têm formato: SERVICE-PROJECT_HASH-REGION.a.run.app
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar se o host termina com .a.run.app (Cloud Run)
        host = request.get_host().split(':')[0]  # Remove porta se houver
        
        # Se for um host do Cloud Run e não estiver em ALLOWED_HOSTS
        if host.endswith('.a.run.app'):
            # Adicionar ao ALLOWED_HOSTS se não estiver lá
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
        
        response = self.get_response(request)
        return response

