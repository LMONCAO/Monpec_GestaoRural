"""
Middleware para proteção contra cópia e acesso não autorizado ao código
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.core.cache import cache
import re


class ProtecaoCodigoMiddleware(MiddlewareMixin):
    """Proteção contra cópia, scraping e acesso não autorizado"""
    
    def process_request(self, request):
        """Verifica requisições suspeitas"""
        from django.conf import settings
        
        # Apenas em produção
        if settings.DEBUG:
            return None
        
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        referer = request.META.get('HTTP_REFERER', '')
        
        # Bloquear user agents suspeitos (scrapers, bots maliciosos)
        user_agents_bloqueados = [
            'scrapy', 'curl', 'wget', 'python-requests', 'httpx',
            'postman', 'insomnia', 'httpie', 'go-http-client',
            'apache-httpclient', 'okhttp', 'java/', 'node-fetch',
        ]
        
        if any(ua in user_agent for ua in user_agents_bloqueados):
            # Verificar se é um bot legítimo (Google, Bing, etc)
            bots_legitimos = ['googlebot', 'bingbot', 'slurp', 'duckduckbot']
            if not any(bot in user_agent for bot in bots_legitimos):
                return self._bloquear_acesso(request, "User agent bloqueado")
        
        # Verificar rate limiting por IP (proteção contra scraping)
        ip_address = self._obter_ip(request)
        cache_key = f"protecao_codigo_rate_limit_{ip_address}"
        tentativas = cache.get(cache_key, 0)
        
        if tentativas > 100:  # Mais de 100 requisições por minuto
            return self._bloquear_acesso(request, "Rate limit excedido")
        
        cache.set(cache_key, tentativas + 1, 60)  # 1 minuto
        
        # Verificar hotlinking (acesso direto a arquivos estáticos de outros sites)
        # IMPORTANTE: Permitir arquivos estáticos do mesmo domínio mesmo sem referer
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            # Se não há referer, provavelmente é uma requisição do mesmo site (permitir)
            if not referer:
                return None  # Permitir arquivos estáticos sem referer (vêm do mesmo site)
            
            # Verificar se o referer é de um domínio permitido
            dominios_permitidos = []
            if settings.ALLOWED_HOSTS:
                dominios_permitidos.extend(settings.ALLOWED_HOSTS)
            dominios_permitidos.extend(['localhost', '127.0.0.1', 'monpec.com.br', 'www.monpec.com.br'])
            
            # Adicionar domínios do Cloud Run
            if hasattr(settings, 'SITE_URL'):
                from urllib.parse import urlparse
                parsed = urlparse(settings.SITE_URL)
                if parsed.netloc:
                    dominios_permitidos.append(parsed.netloc)
            
            # Verificar se o referer é de um domínio permitido
            if not any(dominio in referer for dominio in dominios_permitidos):
                # Hotlinking detectado - bloquear apenas se vier de outro domínio
                return self._bloquear_acesso(request, "Hotlinking não permitido")
        
        return None
    
    def process_response(self, request, response):
        """Adiciona headers de proteção na resposta"""
        from django.conf import settings
        
        # Headers de proteção
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Proteção adicional em produção
        if not settings.DEBUG:
            # Desabilitar cache para páginas sensíveis
            if request.path.startswith('/admin/') or request.path.startswith('/dashboard/'):
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
            
            # Proteção contra MIME sniffing
            response['X-Content-Type-Options'] = 'nosniff'
            
            # CSP (Content Security Policy) - restringe recursos externos
            # Permitir fontes dos ícones (Font Awesome e Bootstrap Icons)
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "media-src 'self' blob:; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            response['Content-Security-Policy'] = csp
        
        return response
    
    def _obter_ip(self, request):
        """Obtém IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def _bloquear_acesso(self, request, motivo):
        """Bloqueia acesso e registra tentativa"""
        from .security_avancado import registrar_log_auditoria
        
        ip_address = self._obter_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Obter usuário de forma segura (pode não estar disponível se AuthenticationMiddleware ainda não processou)
        usuario = None
        if hasattr(request, 'user') and hasattr(request.user, 'is_authenticated'):
            usuario = request.user if request.user.is_authenticated else None
        
        registrar_log_auditoria(
            tipo_acao='ACESSO_NAO_AUTORIZADO',
            descricao=f"Tentativa de acesso bloqueada: {motivo}",
            usuario=usuario,
            ip_address=ip_address,
            user_agent=user_agent,
            nivel_severidade='ALTO',
            sucesso=False,
            metadata={
                'path': request.path,
                'method': request.method,
                'motivo': motivo,
            },
        )
        
        return HttpResponseForbidden("Acesso negado.")







