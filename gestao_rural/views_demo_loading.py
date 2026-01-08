# -*- coding: utf-8 -*-
"""
View para tela de carregamento/criação do sistema personalizado para usuários demo
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)


def demo_loading(request):
    """
    Tela de loading mostrando criação do sistema personalizado para usuários demo.
    Mostra barra de progresso e simulação de prompts de terminal.
    Faz login automático se necessário.
    """
    # Removidos imports desnecessários

    # Verificar se é usuário demo
    # IMPORTANTE: Superusuários e staff nunca são demo
    is_demo_user = False

    if request.user.is_superuser or request.user.is_staff:
        is_demo_user = False
    elif request.user.is_authenticated:
        if request.user.username in ['demo', 'demo_monpec']:
            is_demo_user = True
        else:
            # UsuarioAtivo não existe no banco atual
            # Verificar se é usuário criado recentemente (lógica simplificada)
            try:
                # Usuários demo têm username que começa com email
                if '@' in request.user.username:
                    is_demo_user = True
            except:
                pass
    else:
        # Usuário não logado - tentar encontrar usuário demo recém-criado
        try:
            from .models import Propriedade
            # Procurar pela propriedade demo mais recente
            propriedade_demo = Propriedade.objects.filter(
                nome_propriedade='Fazenda Demonstracao'
            ).order_by('-id').first()

            if propriedade_demo and propriedade_demo.produtor.usuario_responsavel:
                usuario_demo = propriedade_demo.produtor.usuario_responsavel
                # Fazer login automático
                from django.contrib.auth import login
                login(request, usuario_demo)
                logger.info(f'[DEMO_LOADING] Login automático realizado para: {usuario_demo.username}')
                is_demo_user = True
            else:
                logger.warning(f'[DEMO_LOADING] Propriedade demo não encontrada')
                return redirect('login')
        except Exception as e:
            logger.warning(f'[DEMO_LOADING] Erro no login automático: {e}')
            return redirect('login')

    if not is_demo_user:
        logger.warning(f'⚠️ Usuário não demo tentou acessar demo_loading')
        return redirect('dashboard')
    
    # Obter nome do usuário para personalizar
    nome_usuario = request.user.get_full_name() or request.user.username
    
    context = {
        'nome_usuario': nome_usuario,
        'username': request.user.username,
    }
    
    return render(request, 'gestao_rural/demo/demo_loading.html', context)

