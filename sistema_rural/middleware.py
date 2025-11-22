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
        # Obter host diretamente do header HTTP antes da validação do Django
        host = request.META.get('HTTP_HOST', '').split(':')[0]  # Remove porta se houver
        
        # Se não tiver HTTP_HOST, tentar SERVER_NAME
        if not host:
            host = request.META.get('SERVER_NAME', '')
        
        # Se for um host do Cloud Run (qualquer formato) e não estiver em ALLOWED_HOSTS
        if host and (host.endswith('.run.app') or host.endswith('.a.run.app')):
            # Adicionar ao ALLOWED_HOSTS se não estiver lá
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
        
        response = self.get_response(request)
        return response

