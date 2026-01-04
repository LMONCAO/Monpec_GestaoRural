# -*- coding: utf-8 -*-
"""
View de diagnóstico para problemas com imagens
Ajuda a identificar problemas com MEDIA_URL, MEDIA_ROOT, Cloud Storage, etc.
"""

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
import os
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def diagnostico_imagens(request):
    """
    Retorna informações de diagnóstico sobre a configuração de imagens
    """
    diagnostico = {
        'status': 'ok',
        'problemas': [],
        'configuracoes': {},
        'testes': {}
    }
    
    # 1. Verificar MEDIA_URL
    media_url = getattr(settings, 'MEDIA_URL', None)
    diagnostico['configuracoes']['MEDIA_URL'] = media_url
    if not media_url:
        diagnostico['problemas'].append('MEDIA_URL não está configurado')
        diagnostico['status'] = 'erro'
    elif not media_url.startswith('/'):
        diagnostico['problemas'].append('MEDIA_URL deve começar com /')
        diagnostico['status'] = 'erro'
    
    # 2. Verificar MEDIA_ROOT
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    diagnostico['configuracoes']['MEDIA_ROOT'] = str(media_root) if media_root else None
    if not media_root:
        diagnostico['problemas'].append('MEDIA_ROOT não está configurado')
        diagnostico['status'] = 'erro'
    else:
        # Verificar se o diretório existe
        if isinstance(media_root, (str, os.PathLike)):
            media_root_path = str(media_root)
            diagnostico['testes']['MEDIA_ROOT_existe'] = os.path.exists(media_root_path)
            diagnostico['testes']['MEDIA_ROOT_eh_diretorio'] = os.path.isdir(media_root_path) if os.path.exists(media_root_path) else False
            diagnostico['testes']['MEDIA_ROOT_legivel'] = os.access(media_root_path, os.R_OK) if os.path.exists(media_root_path) else False
            diagnostico['testes']['MEDIA_ROOT_gravavel'] = os.access(media_root_path, os.W_OK) if os.path.exists(media_root_path) else False
            
            if not os.path.exists(media_root_path):
                diagnostico['problemas'].append(f'MEDIA_ROOT não existe: {media_root_path}')
                diagnostico['status'] = 'erro'
            elif not os.path.isdir(media_root_path):
                diagnostico['problemas'].append(f'MEDIA_ROOT não é um diretório: {media_root_path}')
                diagnostico['status'] = 'erro'
            elif not os.access(media_root_path, os.R_OK):
                diagnostico['problemas'].append(f'MEDIA_ROOT não é legível: {media_root_path}')
                diagnostico['status'] = 'erro'
    
    # 3. Verificar Cloud Storage
    use_cloud_storage = getattr(settings, 'USE_CLOUD_STORAGE', False)
    diagnostico['configuracoes']['USE_CLOUD_STORAGE'] = use_cloud_storage
    
    if use_cloud_storage:
        default_file_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', None)
        diagnostico['configuracoes']['DEFAULT_FILE_STORAGE'] = default_file_storage
        
        gs_bucket_name = getattr(settings, 'GS_BUCKET_NAME', None)
        diagnostico['configuracoes']['GS_BUCKET_NAME'] = gs_bucket_name
        
        if not default_file_storage:
            diagnostico['problemas'].append('USE_CLOUD_STORAGE=True mas DEFAULT_FILE_STORAGE não está configurado')
            diagnostico['status'] = 'erro'
        elif 'gcloud' not in default_file_storage.lower():
            diagnostico['problemas'].append(f'DEFAULT_FILE_STORAGE não parece ser Cloud Storage: {default_file_storage}')
            diagnostico['status'] = 'aviso'
        
        if not gs_bucket_name:
            diagnostico['problemas'].append('GS_BUCKET_NAME não está configurado')
            diagnostico['status'] = 'erro'
        else:
            # Testar acesso ao Cloud Storage
            try:
                # Tentar listar arquivos no bucket (teste básico)
                test_path = 'test_connection.txt'
                if default_storage.exists(test_path):
                    diagnostico['testes']['cloud_storage_acessivel'] = True
                else:
                    # Tentar criar um arquivo de teste
                    try:
                        default_storage.save(test_path, b'test')
                        default_storage.delete(test_path)
                        diagnostico['testes']['cloud_storage_acessivel'] = True
                        diagnostico['testes']['cloud_storage_gravavel'] = True
                    except Exception as e:
                        diagnostico['testes']['cloud_storage_acessivel'] = False
                        diagnostico['problemas'].append(f'Erro ao acessar Cloud Storage: {str(e)}')
                        diagnostico['status'] = 'erro'
            except Exception as e:
                diagnostico['testes']['cloud_storage_acessivel'] = False
                diagnostico['problemas'].append(f'Erro ao testar Cloud Storage: {str(e)}')
                diagnostico['status'] = 'erro'
    else:
        diagnostico['configuracoes']['armazenamento'] = 'sistema_de_arquivos_local'
        diagnostico['aviso'] = 'Usando sistema de arquivos local. No Cloud Run, arquivos podem ser perdidos quando o container reinicia. Considere usar Cloud Storage.'
    
    # 4. Verificar rota de mídia
    from django.urls import reverse
    try:
        media_url_pattern = reverse('serve_media', args=['test.jpg'])
        diagnostico['testes']['rota_media_disponivel'] = True
        diagnostico['testes']['rota_media_url'] = media_url_pattern
    except Exception as e:
        diagnostico['testes']['rota_media_disponivel'] = False
        diagnostico['problemas'].append(f'Rota serve_media não encontrada: {str(e)}')
        diagnostico['status'] = 'erro'
    
    # 5. Verificar se há arquivos de mídia
    if media_root and os.path.exists(str(media_root)):
        try:
            arquivos_media = []
            for root, dirs, files in os.walk(str(media_root)):
                for file in files[:10]:  # Limitar a 10 arquivos para não sobrecarregar
                    arquivos_media.append(os.path.relpath(os.path.join(root, file), str(media_root)))
            diagnostico['testes']['arquivos_encontrados'] = len(arquivos_media)
            diagnostico['testes']['exemplos_arquivos'] = arquivos_media[:5]  # Mostrar apenas 5 exemplos
        except Exception as e:
            diagnostico['problemas'].append(f'Erro ao listar arquivos de mídia: {str(e)}')
    
    # 6. Verificar STATIC_URL (para comparação)
    static_url = getattr(settings, 'STATIC_URL', None)
    diagnostico['configuracoes']['STATIC_URL'] = static_url
    
    # Resumo
    if diagnostico['status'] == 'ok' and len(diagnostico['problemas']) == 0:
        diagnostico['mensagem'] = '✅ Configuração de imagens parece estar correta'
    elif diagnostico['status'] == 'erro':
        diagnostico['mensagem'] = f'❌ Encontrados {len(diagnostico["problemas"])} problema(s) crítico(s)'
    else:
        diagnostico['mensagem'] = f'⚠️ Encontrados {len(diagnostico["problemas"])} aviso(s)'
    
    return JsonResponse(diagnostico, json_dumps_params={'indent': 2, 'ensure_ascii': False})
