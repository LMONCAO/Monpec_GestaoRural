# -*- coding: utf-8 -*-
"""
View para servir arquivos media (fotos, uploads) em produção
"""

from django.conf import settings
from django.http import Http404, FileResponse
from django.views.decorators.cache import cache_control
import os
import logging

logger = logging.getLogger(__name__)


@cache_control(max_age=3600)  # Cache por 1 hora
def serve_media(request, path):
    """
    Serve arquivos de media em produção (Cloud Run).
    WhiteNoise serve apenas static files, então media files precisam ser servidos manualmente.
    """
    # Construir caminho completo do arquivo
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if not media_root:
        logger.error('MEDIA_ROOT não está configurado')
        raise Http404('Media root não configurado')
    
    file_path = os.path.join(media_root, path)
    
    # Verificar se o arquivo existe e está dentro do media_root (segurança)
    if not os.path.exists(file_path) or not file_path.startswith(os.path.abspath(media_root)):
        logger.warning(f'Arquivo não encontrado ou fora do media_root: {path}')
        raise Http404('Arquivo não encontrado')
    
    # Verificar se é um arquivo (não diretório)
    if not os.path.isfile(file_path):
        logger.warning(f'Caminho não é um arquivo: {path}')
        raise Http404('Caminho não é um arquivo')
    
    # Determinar content-type baseado na extensão
    import mimetypes
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = 'application/octet-stream'
    
    # Servir o arquivo
    try:
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        # Adicionar headers de segurança
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    except IOError:
        logger.error(f'Erro ao abrir arquivo: {file_path}')
        raise Http404('Erro ao abrir arquivo')

