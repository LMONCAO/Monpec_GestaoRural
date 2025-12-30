# -*- coding: utf-8 -*-
"""
View customizada para servir arquivos estáticos manualmente
Garante que arquivos estáticos sejam servidos mesmo se a configuração padrão falhar
"""
from django.http import FileResponse, Http404
from django.conf import settings
from pathlib import Path
import os


def serve_static_file(request, path):
    """
    Serve arquivos estáticos manualmente.
    Útil quando a configuração padrão do Django não funciona.
    """
    # Obter o diretório de arquivos estáticos
    if settings.STATICFILES_DIRS:
        static_root = Path(settings.STATICFILES_DIRS[0])
    else:
        static_root = Path(settings.BASE_DIR) / 'static'
    
    # Construir o caminho completo do arquivo
    file_path = static_root / path
    
    # Verificar se o arquivo existe
    if not file_path.exists():
        raise Http404(f'Arquivo não encontrado: {path}')
    
    # Verificar se o caminho está dentro do diretório static (segurança)
    try:
        file_path.resolve().relative_to(static_root.resolve())
    except ValueError:
        raise Http404('Acesso negado')
    
    # Determinar o tipo MIME
    content_type = 'application/octet-stream'
    if path.endswith('.jpeg') or path.endswith('.jpg'):
        content_type = 'image/jpeg'
    elif path.endswith('.png'):
        content_type = 'image/png'
    elif path.endswith('.gif'):
        content_type = 'image/gif'
    elif path.endswith('.css'):
        content_type = 'text/css'
    elif path.endswith('.js'):
        content_type = 'application/javascript'
    
    # Servir o arquivo
    return FileResponse(
        open(file_path, 'rb'),
        content_type=content_type
    )
