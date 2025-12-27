# -*- coding: utf-8 -*-
"""
View para tela de carregamento/criação do sistema personalizado para usuários demo
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)


@login_required
def demo_loading(request):
    """
    Tela de loading mostrando criação do sistema personalizado para usuários demo.
    Mostra barra de progresso e simulação de prompts de terminal.
    """
    # Verificar se é usuário demo
    is_demo_user = False
    if request.user.username in ['demo', 'demo_monpec']:
        is_demo_user = True
    else:
        try:
            from .models_auditoria import UsuarioAtivo
            UsuarioAtivo.objects.get(usuario=request.user)
            is_demo_user = True
        except:
            pass
    
    if not is_demo_user:
        logger.warning(f'⚠️ Usuário não demo tentou acessar demo_loading: {request.user.username}')
        return redirect('dashboard')
    
    # Obter nome do usuário para personalizar
    nome_usuario = request.user.get_full_name() or request.user.username
    
    context = {
        'nome_usuario': nome_usuario,
        'username': request.user.username,
    }
    
    return render(request, 'gestao_rural/demo/demo_loading.html', context)

