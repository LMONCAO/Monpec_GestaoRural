"""
Middleware de segurança avançada
Verifica sessões seguras e registra atividades suspeitas
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

from .security_avancado import (
    verificar_sessao_segura,
    registrar_log_auditoria,
    obter_ip_address,
)


class SegurancaAvancadaMiddleware(MiddlewareMixin):
    """Middleware para verificação de segurança em cada requisição"""
    
    def process_request(self, request):
        """Processa cada requisição verificando segurança"""
        # Ignorar URLs públicas
        urls_publicas = [
            '/login/',
            '/recuperar-senha/',
            '/verificar-email/',
            '/admin/login/',
            '/static/',
            '/media/',
        ]
        
        if any(request.path.startswith(url) for url in urls_publicas):
            return None
        
        # Verificar apenas usuários autenticados
        if not request.user.is_authenticated:
            return None
        
        # Verificar sessão segura (apenas se já tiver sessão criada)
        if request.session.session_key:
            ip_address = obter_ip_address(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Registrar ou atualizar sessão segura
            from .security_avancado import registrar_sessao_segura
            registrar_sessao_segura(request.user, request.session.session_key, ip_address, user_agent)
            
            # Verificar se sessão é válida
            sessao_valida = verificar_sessao_segura(
                request.user,
                request.session.session_key,
                ip_address
            )
            
            if not sessao_valida:
                # Sessão inválida ou IP mudou - logout forçado
                registrar_log_auditoria(
                    tipo_acao='ACESSO_NAO_AUTORIZADO',
                    descricao=f"Mudança de IP detectada - logout forçado",
                    usuario=request.user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    nivel_severidade='CRITICO',
                    sucesso=False,
                )
                logout(request)
                messages.error(
                    request,
                    'Mudança de IP detectada. Por segurança, você foi desconectado. Faça login novamente.'
                )
                return redirect('login')
        
        return None

