"""
Middleware de segurança para o sistema MONPEC
Implementa rate limiting e outras proteções
"""
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware para limitar requisições por IP
    """
    def process_request(self, request):
        # Aplica rate limiting apenas em views de login
        if request.path.startswith('/login') or request.path.startswith('/admin/login'):
            ip_address = self.get_client_ip(request)
            chave = f'rate_limit_{ip_address}'
            
            # Limite: 20 requisições por minuto
            tentativas = cache.get(chave, 0)
            if tentativas >= 20:
                logger.warning(f'Rate limit excedido para IP: {ip_address}')
                return HttpResponseForbidden(
                    'Muitas requisições. Tente novamente em alguns minutos.',
                    content_type='text/plain'
                )
            
            cache.set(chave, tentativas + 1, 60)  # Expira em 1 minuto
        
        return None
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adiciona headers de segurança HTTP
    """
    def process_response(self, request, response):
        # Previne clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Previne MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer Policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response







