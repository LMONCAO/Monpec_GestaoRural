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
    Verifica primeiro em STATIC_ROOT (produção) e depois em STATICFILES_DIRS (desenvolvimento).
    """
    file_path = None
    static_root = None
    
    # Prioridade 1: Verificar em STATIC_ROOT (arquivos coletados em produção)
    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        static_root = Path(settings.STATIC_ROOT)
        file_path = static_root / path
        if file_path.exists() and file_path.is_file():
            # Verificar segurança: arquivo deve estar dentro de STATIC_ROOT
            try:
                file_path.resolve().relative_to(static_root.resolve())
            except ValueError:
                file_path = None
            else:
                # Arquivo encontrado em STATIC_ROOT
                pass
    
    # Prioridade 2: Se não encontrou em STATIC_ROOT, verificar em STATICFILES_DIRS
    if file_path is None or not file_path.exists():
        if settings.STATICFILES_DIRS:
            static_root = Path(settings.STATICFILES_DIRS[0])
        else:
            static_root = Path(settings.BASE_DIR) / 'static'
        
        file_path = static_root / path
        
        # Verificar segurança: arquivo deve estar dentro do diretório static
        if file_path.exists():
            try:
                file_path.resolve().relative_to(static_root.resolve())
            except ValueError:
                file_path = None
    
    # Se ainda não encontrou, retornar 404
    if file_path is None or not file_path.exists() or not file_path.is_file():
        raise Http404(f'Arquivo não encontrado: {path}')
    
    # Determinar o tipo MIME baseado na extensão
    import mimetypes
    content_type, _ = mimetypes.guess_type(str(file_path))
    if not content_type:
        # Fallback para tipos comuns
        path_lower = path.lower()
        if path_lower.endswith(('.jpeg', '.jpg')):
            content_type = 'image/jpeg'
        elif path_lower.endswith('.png'):
            content_type = 'image/png'
        elif path_lower.endswith('.gif'):
            content_type = 'image/gif'
        elif path_lower.endswith('.webp'):
            content_type = 'image/webp'
        elif path_lower.endswith('.svg'):
            content_type = 'image/svg+xml'
        elif path_lower.endswith('.css'):
            content_type = 'text/css'
        elif path_lower.endswith('.js'):
            content_type = 'application/javascript'
        elif path_lower.endswith('.json'):
            content_type = 'application/json'
        else:
            content_type = 'application/octet-stream'
    
    # Servir o arquivo
    # FileResponse fecha o arquivo automaticamente quando a resposta é enviada
    response = FileResponse(
        open(file_path, 'rb'),
        content_type=content_type
    )
    
    # Adicionar headers de cache para imagens
    if content_type.startswith('image/'):
        response['Cache-Control'] = 'public, max-age=31536000'  # 1 ano para imagens
    
    return response
