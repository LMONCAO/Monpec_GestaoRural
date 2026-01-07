"""
Middleware customizado para permitir hosts do Cloud Run e Fly.io dinamicamente.
"""
from django.conf import settings
from django.core.exceptions import DisallowedHost
import logging
import os
import re

logger = logging.getLogger(__name__)


class FlyIOHostMiddleware:
    """
    Middleware para permitir IPs internos do Fly.io dinamicamente.
    Fly.io usa IPs na faixa 172.x.x.x para health checks internos.
    
    Este middleware deve ser o PRIMEIRO na lista de middlewares para interceptar
    antes da validação padrão do Django.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """
        Processa a requisição ANTES de qualquer outro middleware.
        Permite IPs internos do Fly.io (172.x.x.x) para health checks.
        """
        # Obter host diretamente do header HTTP ANTES de qualquer validação
        host = request.META.get('HTTP_HOST', '').split(':')[0]  # Remove porta se houver
        
        # Se não tiver HTTP_HOST, tentar SERVER_NAME
        if not host:
            host = request.META.get('SERVER_NAME', '')
        
        # Verificar se é um IP interno do Fly.io (172.x.x.x)
        if host and re.match(r'^172\.\d{1,3}\.\d{1,3}\.\d{1,3}$', host):
            # É um IP interno do Fly.io - permitir
            # Adicionar dinamicamente ao ALLOWED_HOSTS se não estiver lá
            if host not in settings.ALLOWED_HOSTS:
                settings.ALLOWED_HOSTS.append(host)
                logger.info(f"✅ IP interno do Fly.io adicionado ao ALLOWED_HOSTS: {host}")
        
        return None

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)


class CloudRunHostMiddleware:
    """
    Middleware para permitir hosts do Cloud Run dinamicamente.
    Cloud Run URLs têm formato: SERVICE-PROJECT_HASH-REGION.a.run.app
    
    Este middleware deve ser o PRIMEIRO na lista de middlewares para interceptar
    antes da validação padrão do Django.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        """
        Processa a requisição ANTES de qualquer outro middleware.
        Isso garante que o host seja adicionado ao ALLOWED_HOSTS antes
        do CommonMiddleware validar.
        """
        # CRÍTICO: Não usar request.get_host() aqui pois ele já valida ALLOWED_HOSTS
        # Obter host diretamente do header HTTP ANTES de qualquer validação
        host = request.META.get('HTTP_HOST', '').split(':')[0]  # Remove porta se houver
        
        # Se não tiver HTTP_HOST, tentar SERVER_NAME
        if not host:
            host = request.META.get('SERVER_NAME', '')
        
        # Se for um host do Cloud Run (qualquer formato), adicionar ao ALLOWED_HOSTS e CSRF_TRUSTED_ORIGINS
        if host:
            # Verificar se é um host do Cloud Run
            is_cloud_run = host.endswith('.run.app') or host.endswith('.a.run.app')
            
            # Se for Cloud Run ou localhost, adicionar ao ALLOWED_HOSTS
            if is_cloud_run or host in ['localhost', '127.0.0.1', '0.0.0.0']:
                # Adicionar ao ALLOWED_HOSTS se não estiver lá
                if host not in settings.ALLOWED_HOSTS:
                    # Modificar a lista diretamente
                    if isinstance(settings.ALLOWED_HOSTS, list):
                        settings.ALLOWED_HOSTS.append(host)
                        logger.info(f"✅ Adicionado host ao ALLOWED_HOSTS: {host}")
                    # Se for uma tupla ou outro tipo, converter para lista
                    elif hasattr(settings.ALLOWED_HOSTS, '__iter__'):
                        settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + [host]
                        logger.info(f"✅ Adicionado host ao ALLOWED_HOSTS: {host}")
                
                # Adicionar ao CSRF_TRUSTED_ORIGINS se não estiver lá
                # Determinar o protocolo (https para Cloud Run, http para localhost)
                protocol = 'https' if is_cloud_run else 'http'
                origin = f'{protocol}://{host}'
                
                if isinstance(settings.CSRF_TRUSTED_ORIGINS, list):
                    if origin not in settings.CSRF_TRUSTED_ORIGINS:
                        settings.CSRF_TRUSTED_ORIGINS.append(origin)
                        logger.info(f"✅ Adicionado origem ao CSRF_TRUSTED_ORIGINS: {origin}")
                elif hasattr(settings.CSRF_TRUSTED_ORIGINS, '__iter__'):
                    if origin not in settings.CSRF_TRUSTED_ORIGINS:
                        settings.CSRF_TRUSTED_ORIGINS = list(settings.CSRF_TRUSTED_ORIGINS) + [origin]
                        logger.info(f"✅ Adicionado origem ao CSRF_TRUSTED_ORIGINS: {origin}")
        
        # Retornar None para continuar o processamento normal
        return None

    def __call__(self, request):
        # Chamar process_request primeiro
        response = self.process_request(request)
        if response is not None:
            return response
        
        # Processar a requisição normalmente
        try:
            response = self.get_response(request)
            return response
        except DisallowedHost as e:
            # Se ainda assim der erro, tentar adicionar o host novamente
            host = request.META.get('HTTP_HOST', '').split(':')[0]
            if host and host not in settings.ALLOWED_HOSTS:
                if isinstance(settings.ALLOWED_HOSTS, list):
                    settings.ALLOWED_HOSTS.append(host)
                    logger.warning(f"⚠️ Host bloqueado, adicionando ao ALLOWED_HOSTS: {host}")
                    # Tentar novamente
                    try:
                        response = self.get_response(request)
                        return response
                    except DisallowedHost:
                        logger.error(f"❌ Falha ao processar host: {host}")
                        raise
            raise

