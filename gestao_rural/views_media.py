# -*- coding: utf-8 -*-
"""
View para servir arquivos media (fotos, uploads) em produção
Suporta tanto sistema de arquivos local quanto Cloud Storage
"""

from django.conf import settings
from django.http import Http404, FileResponse, HttpResponse
from django.views.decorators.cache import cache_control
from django.core.files.storage import default_storage
import os
import logging

logger = logging.getLogger(__name__)


@cache_control(max_age=3600)  # Cache por 1 hora
def serve_media(request, path):
    """
    Serve arquivos de media em produção (Cloud Run).
    Suporta:
    - Sistema de arquivos local (quando não usa Cloud Storage)
    - Cloud Storage (quando USE_CLOUD_STORAGE=True)
    """
    logger.info(f'🔍 Tentando servir arquivo de mídia: {path}')
    
    # Verificar se está usando Cloud Storage
    use_cloud_storage = getattr(settings, 'USE_CLOUD_STORAGE', False)
    default_file_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', None)
    
    if use_cloud_storage or (default_file_storage and 'gcloud' in default_file_storage.lower()):
        # Usar Cloud Storage
        logger.info(f'📦 Usando Cloud Storage para servir: {path}')
        try:
            # Verificar se o arquivo existe no Cloud Storage
            if default_storage.exists(path):
                # Abrir arquivo do Cloud Storage
                file = default_storage.open(path, 'rb')
                content = file.read()
                file.close()
                
                # Determinar content-type
                import mimetypes
                content_type, _ = mimetypes.guess_type(path)
                if not content_type:
                    content_type = 'application/octet-stream'
                
                # Criar resposta
                response = HttpResponse(content, content_type=content_type)
                response['X-Content-Type-Options'] = 'nosniff'
                response['Cache-Control'] = 'public, max-age=3600'
                logger.info(f'✅ Arquivo servido do Cloud Storage: {path}')
                return response
            else:
                logger.warning(f'❌ Arquivo não encontrado no Cloud Storage: {path}')
                raise Http404('Arquivo não encontrado no Cloud Storage')
        except Exception as e:
            logger.error(f'❌ Erro ao servir arquivo do Cloud Storage: {path} - {str(e)}')
            raise Http404(f'Erro ao servir arquivo: {str(e)}')
    else:
        # Usar sistema de arquivos local
        logger.info(f'📁 Usando sistema de arquivos local para servir: {path}')
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if not media_root:
            logger.error('❌ MEDIA_ROOT não está configurado')
            raise Http404('Media root não configurado')
        
        # Garantir que media_root seja um Path object ou string
        if hasattr(media_root, '__fspath__'):
            media_root = str(media_root)
        
        file_path = os.path.join(media_root, path)
        
        # Normalizar caminho para segurança
        file_path = os.path.normpath(file_path)
        media_root_abs = os.path.abspath(media_root)
        
        # Verificar se o arquivo está dentro do media_root (segurança)
        if not file_path.startswith(media_root_abs):
            logger.warning(f'⚠️ Tentativa de acesso fora do media_root: {path}')
            raise Http404('Acesso negado')
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            logger.warning(f'❌ Arquivo não encontrado: {file_path} (path solicitado: {path})')
            logger.info(f'   MEDIA_ROOT: {media_root}')
            logger.info(f'   Caminho completo: {file_path}')
            raise Http404('Arquivo não encontrado')
        
        # Verificar se é um arquivo (não diretório)
        if not os.path.isfile(file_path):
            logger.warning(f'⚠️ Caminho não é um arquivo: {file_path}')
            raise Http404('Caminho não é um arquivo')
        
        # Determinar content-type baseado na extensão
        import mimetypes
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Servir o arquivo
        try:
            file_handle = open(file_path, 'rb')
            response = FileResponse(file_handle, content_type=content_type)
            # Adicionar headers de segurança
            response['X-Content-Type-Options'] = 'nosniff'
            response['Cache-Control'] = 'public, max-age=3600'
            logger.info(f'✅ Arquivo servido do sistema de arquivos: {file_path}')
            return response
        except IOError as e:
            logger.error(f'❌ Erro ao abrir arquivo: {file_path} - {str(e)}')
            raise Http404('Erro ao abrir arquivo')


