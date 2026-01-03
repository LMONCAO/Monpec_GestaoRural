# -*- coding: utf-8 -*-
"""
View de debug para verificar arquivos estáticos
"""
from django.http import JsonResponse
from django.conf import settings
import os
from pathlib import Path

def debug_static_files(request):
    """Verifica se os arquivos estáticos existem"""
    info = {
        'STATIC_ROOT': str(getattr(settings, 'STATIC_ROOT', 'NÃO DEFINIDO')),
        'STATIC_URL': getattr(settings, 'STATIC_URL', 'NÃO DEFINIDO'),
        'WHITENOISE_ROOT': str(getattr(settings, 'WHITENOISE_ROOT', 'NÃO DEFINIDO')),
        'STATICFILES_DIRS': [str(d) for d in getattr(settings, 'STATICFILES_DIRS', [])],
        'white_noise_active': 'whitenoise.middleware.WhiteNoiseMiddleware' in getattr(settings, 'MIDDLEWARE', []),
        'files_in_static_root': {},
        'files_in_static_dirs': {},
    }
    
    # Verificar arquivos em STATIC_ROOT
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root:
        static_root_path = Path(static_root)
        if static_root_path.exists():
            site_dir = static_root_path / 'site'
            if site_dir.exists():
                for i in range(1, 7):
                    foto_file = site_dir / f'foto{i}.jpeg'
                    info['files_in_static_root'][f'foto{i}.jpeg'] = {
                        'exists': foto_file.exists(),
                        'path': str(foto_file),
                        'size': foto_file.stat().st_size if foto_file.exists() else 0,
                    }
            else:
                info['files_in_static_root']['error'] = f'Diretório {site_dir} não existe'
        else:
            info['files_in_static_root']['error'] = f'STATIC_ROOT {static_root} não existe'
    
    # Verificar arquivos em STATICFILES_DIRS
    staticfiles_dirs = getattr(settings, 'STATICFILES_DIRS', [])
    for static_dir in staticfiles_dirs:
        static_dir_path = Path(static_dir)
        if static_dir_path.exists():
            site_dir = static_dir_path / 'site'
            if site_dir.exists():
                for i in range(1, 7):
                    foto_file = site_dir / f'foto{i}.jpeg'
                    info['files_in_static_dirs'][str(static_dir)][f'foto{i}.jpeg'] = {
                        'exists': foto_file.exists(),
                        'path': str(foto_file),
                        'size': foto_file.stat().st_size if foto_file.exists() else 0,
                    }
    
    return JsonResponse(info, indent=2)

