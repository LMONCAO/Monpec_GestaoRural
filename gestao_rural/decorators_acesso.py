"""
Decorators para controle de acesso baseado em assinatura.
Não redireciona automaticamente - apenas marca no request para uso nas views.
"""

from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .models import AssinaturaCliente


def verificar_acesso_assinatura(view_func):
    """
    Decorator que verifica se o usuário tem acesso liberado.
    Se não tiver, adiciona mensagem mas NÃO redireciona automaticamente.
    O redirecionamento só acontece quando o usuário clicar no botão.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Superusuários e staff sempre têm acesso
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        # Verificar se tem assinatura e acesso liberado
        # O middleware já adicionou isso no request
        acesso_liberado = getattr(request, 'acesso_liberado', True)
        assinatura = getattr(request, 'assinatura', None)
        
        # Se não tem acesso liberado, adicionar mensagem mas permitir visualizar
        # O template mostrará o banner e o botão para assinar
        if not acesso_liberado:
            if assinatura and assinatura.data_liberacao:
                data_formatada = assinatura.data_liberacao.strftime('%d/%m/%Y')
                messages.info(
                    request,
                    f'Seu acesso será liberado em {data_formatada}. '
                    f'Seu pagamento foi confirmado e está aguardando a data de liberação.'
                )
            elif not assinatura:
                messages.warning(
                    request,
                    'Você precisa assinar um plano para acessar todas as funcionalidades. '
                    'Clique em "Garanta sua assinatura agora" no topo da página.'
                )
            else:
                messages.warning(
                    request,
                    'Aguardando confirmação do pagamento. '
                    'Você receberá um e-mail quando seu acesso for liberado.'
                )
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
































