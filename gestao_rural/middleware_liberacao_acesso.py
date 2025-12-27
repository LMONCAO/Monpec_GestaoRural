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
        
        # Importar função helper para verificar se é assinante
        from .helpers_acesso import is_usuario_assinante
        
        # Verificar se é admin ou assinante - se for, liberar acesso completo
        if is_usuario_assinante(request.user):
            # Admin ou assinante com acesso liberado - permitir acesso completo
            try:
                assinatura = AssinaturaCliente.objects.select_related('plano').filter(usuario=request.user).first()
                request.assinatura = assinatura
                request.acesso_liberado = True
            except:
                request.assinatura = None
                request.acesso_liberado = True  # Admin sempre tem acesso
            return None  # Permitir acesso completo
        
        # Verificar se é usuário demo PRIMEIRO (antes de verificar assinatura)
        # Usuários criados pelo botão demonstração (com UsuarioAtivo) devem ser tratados como demo padrão
        is_demo_user = False
        if request.user.username in ['demo', 'demo_monpec']:
            is_demo_user = True
        else:
            try:
                from .models_auditoria import UsuarioAtivo
                UsuarioAtivo.objects.get(usuario=request.user)
                is_demo_user = True  # Usuário criado pelo botão demonstração = mesmo comportamento que demo padrão
            except:
                pass
        
        # Se for usuário demo, tratar como pré-lançamento (bloquear módulos)
        if is_demo_user:
            request.assinatura = None
            request.acesso_liberado = False  # Usuários demo têm acesso restrito
            # Permitir acesso apenas a algumas rotas específicas
            if not any(request.path.startswith(path) for path in [
                '/propriedade/', '/dashboard/', '/demo/setup/', 
                '/login/', '/logout/', '/static/', '/media/'
            ]):
                return None  # Continuar normalmente, mas acesso_liberado será False
            return None
        
        # Verificar se o usuário tem assinatura (mas não é assinante ativo)
        try:
            assinatura = AssinaturaCliente.objects.select_related('plano').get(usuario=request.user)
            request.assinatura = assinatura
            
            # Se tiver assinatura ativa mas não passou na verificação de is_usuario_assinante,
            # significa que não tem acesso_liberado = True
            if assinatura.status == AssinaturaCliente.Status.ATIVA and not assinatura.acesso_liberado:
                # Assinatura ativa mas sem acesso liberado ainda - pode estar aguardando data de liberação
                request.acesso_liberado = False
            elif assinatura.status == AssinaturaCliente.Status.ATIVA and assinatura.acesso_liberado:
                # Se chegou aqui e tem acesso_liberado, deveria ter passado na verificação acima
                # Mas por segurança, permitir acesso
                request.acesso_liberado = True
            else:
                request.acesso_liberado = False
        except AssinaturaCliente.DoesNotExist:
            # Usuário sem assinatura - marcar no request
            request.assinatura = None
            request.acesso_liberado = False
        
        return None

