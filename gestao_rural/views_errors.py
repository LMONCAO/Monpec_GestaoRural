# -*- coding: utf-8 -*-
"""
Views customizadas para tratamento de erros HTTP
"""

from django.shortcuts import redirect
from django.http import HttpResponseServerError
import logging

logger = logging.getLogger(__name__)


def handler500(request):
    """
    Handler customizado para erro 500.
    Redireciona para a página inicial (dashboard) ao invés de mostrar página de erro.
    """
    logger.error('Erro 500 detectado. Redirecionando para dashboard.')
    
    # Tentar redirecionar para dashboard
    # O dashboard por sua vez redireciona para propriedade_modulos se houver propriedades
    return redirect('dashboard')


