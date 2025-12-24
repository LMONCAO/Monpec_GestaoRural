"""
Middleware para controlar liberação de acesso baseado na data de liberação da assinatura.
Usuários só terão acesso após a data_liberacao definida na assinatura.
"""

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from .models import AssinaturaCliente


class LiberacaoAcessoMiddleware(MiddlewareMixin):
    """
    Middleware que verifica se o usuário tem acesso liberado baseado na data_liberacao.
    """
    
    def process_request(self, request):
        """Verifica se o acesso está liberado para o usuário."""
        
        # URLs públicas que não precisam de verificação
        urls_publicas = [
            '/login/',
            '/logout/',
            '/recuperar-senha/',
            '/verificar-email/',
            '/admin/login/',
            '/static/',
            '/media/',
            '/assinaturas/',  # Página de assinaturas sempre acessível
            '/assinaturas/sucesso/',
            '/assinaturas/cancelado/',
            '/assinaturas/webhook/',
            '/pre-lancamento/',  # Página de pré-lançamento
        ]
        
        # Verificar se é URL pública
        if any(request.path.startswith(url) for url in urls_publicas):
            return None
        
        # Verificar apenas usuários autenticados
        if not request.user.is_authenticated:
            return None
        
        # Superusuários e staff sempre têm acesso
        if request.user.is_superuser or request.user.is_staff:
            return None
        
        # Verificar se o usuário tem assinatura
        try:
            assinatura = AssinaturaCliente.objects.select_related('plano').get(usuario=request.user)
            request.assinatura = assinatura
            
            # SEMPRE redirecionar assinantes para a página de pré-lançamento
            # Mesmo que tenham assinatura ativa, o sistema está em pré-lançamento
            if assinatura.status == AssinaturaCliente.Status.ATIVA:
                # Redirecionar para página de pré-lançamento
                from django.contrib import messages
                messages.info(
                    request,
                    f"Bem-vindo, {request.user.get_full_name() or request.user.username}! "
                    "Aguarde o lançamento em 01/02/2026. Um consultor entrará em contato em breve."
                )
                return redirect('pre_lancamento')
            
            request.acesso_liberado = False
        except AssinaturaCliente.DoesNotExist:
            # Usuário sem assinatura - marcar no request
            request.assinatura = None
            request.acesso_liberado = False
        
        return None

