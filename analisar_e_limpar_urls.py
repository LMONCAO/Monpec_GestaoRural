#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para analisar e limpar URLs não utilizadas do sistema
"""

import os
import sys
import re
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
import django
django.setup()

from django.urls import get_resolver
from django.conf import settings

def coletar_todas_urls():
    """Coleta todas as URLs do sistema"""
    resolver = get_resolver()
    urls = {}
    
    def percorrer_patterns(patterns, prefix=''):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                # É um include
                new_prefix = prefix + str(pattern.pattern)
                percorrer_patterns(pattern.url_patterns, new_prefix)
            else:
                # É uma URL
                pattern_str = str(pattern.pattern)
                full_path = prefix + pattern_str
                
                if hasattr(pattern, 'name') and pattern.name:
                    view_name = 'N/A'
                    if hasattr(pattern, 'callback'):
                        if callable(pattern.callback):
                            if hasattr(pattern.callback, '__name__'):
                                view_name = pattern.callback.__name__
                            elif hasattr(pattern.callback, 'view_class'):
                                view_name = pattern.callback.view_class.__name__
                    
                    urls[pattern.name] = {
                        'path': full_path,
                        'view': view_name,
                        'pattern': pattern
                    }
    
    percorrer_patterns(resolver.url_patterns)
    return urls

def buscar_referencias(urls_dict):
    """Busca referências a URLs em templates, código Python e JavaScript"""
    referencias = {url_name: [] for url_name in urls_dict.keys()}
    base_dir = Path(settings.BASE_DIR)
    
    # Buscar em templates HTML
    print("Buscando referencias em templates...")
    for template_file in base_dir.rglob('*.html'):
        if 'node_modules' in str(template_file) or '__pycache__' in str(template_file):
            continue
        try:
            content = template_file.read_text(encoding='utf-8', errors='ignore')
            for url_name, url_info in urls_dict.items():
                # Buscar {% url 'nome' %}
                if f"url '{url_name}'" in content or f'url "{url_name}"' in content:
                    referencias[url_name].append(f"template:{template_file.relative_to(base_dir)}")
                # Buscar reverse('nome')
                if f"reverse('{url_name}'" in content or f'reverse("{url_name}"' in content:
                    referencias[url_name].append(f"template:{template_file.relative_to(base_dir)}")
        except:
            pass
    
    # Buscar em código Python
    print("Buscando referencias em codigo Python...")
    for py_file in base_dir.rglob('*.py'):
        if 'migrations' in str(py_file) or '__pycache__' in str(py_file) or 'venv' in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            for url_name, url_info in urls_dict.items():
                # Buscar reverse('nome')
                if f"reverse('{url_name}'" in content or f'reverse("{url_name}"' in content:
                    referencias[url_name].append(f"python:{py_file.relative_to(base_dir)}")
                # Buscar redirect('nome')
                if f"redirect('{url_name}'" in content or f'redirect("{url_name}"' in content:
                    referencias[url_name].append(f"python:{py_file.relative_to(base_dir)}")
                # Buscar get_absolute_url ou similar
                if f"'{url_name}'" in content and ('reverse' in content or 'redirect' in content):
                    # Verificar contexto
                    if f"name='{url_name}'" in content or f'name="{url_name}"' in content:
                        referencias[url_name].append(f"python:{py_file.relative_to(base_dir)}")
        except:
            pass
    
    # Buscar em JavaScript
    print("Buscando referencias em JavaScript...")
    for js_file in base_dir.rglob('*.js'):
        if 'node_modules' in str(js_file) or '__pycache__' in str(js_file):
            continue
        try:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            for url_name, url_info in urls_dict.items():
                # Buscar URLs em strings JavaScript (caminho completo)
                url_path = url_info['path'].replace('<int:', '').replace('<str:', '').replace('<slug:', '').replace('>', '')
                if url_path in content and ('fetch' in content or 'axios' in content or 'window.location' in content):
                    referencias[url_name].append(f"js:{js_file.relative_to(base_dir)}")
        except:
            pass
    
    return referencias

def verificar_views_existentes(urls_dict):
    """Verifica se as views referenciadas existem"""
    views_existentes = {}
    
    for url_name, url_info in urls_dict.items():
        view_name = url_info.get('view', '')
        if view_name == 'N/A':
            # Tentar verificar pelo callback
            try:
                pattern = url_info['pattern']
                if hasattr(pattern, 'callback') and pattern.callback:
                    views_existentes[url_name] = True
                else:
                    views_existentes[url_name] = False
            except:
                views_existentes[url_name] = True  # Assumir OK
        else:
            views_existentes[url_name] = True  # Se tem nome, assumir que existe
    
    return views_existentes

def main():
    print("=" * 70)
    print("ANALISE DE URLs DO SISTEMA")
    print("=" * 70)
    
    # 1. Coletar todas as URLs
    print("\n1. Coletando todas as URLs...")
    todas_urls = coletar_todas_urls()
    print(f"   Total de URLs encontradas: {len(todas_urls)}")
    
    # 2. Verificar views existentes
    print("\n2. Verificando views existentes...")
    views_existentes = verificar_views_existentes(todas_urls)
    
    # 3. Buscar referências
    print("\n3. Buscando referencias...")
    referencias = buscar_referencias(todas_urls)
    
    # 4. Identificar URLs não utilizadas
    print("\n4. Analisando URLs...")
    
    urls_criticas = {
        'login', 'logout', 'dashboard', 'landing_page', 'admin',
        'health_check', 'sitemap', 'password_reset', 'password_reset_done',
        'password_reset_confirm', 'password_reset_complete',
        'mercadopago_webhook', 'whatsapp_webhook',  # Webhooks são chamados externamente
    }
    
    urls_nao_utilizadas = []
    urls_utilizadas = []
    urls_api_webhook = []
    
    for url_name, url_info in todas_urls.items():
        view_existe = views_existentes.get(url_name, False)
        tem_referencias = len(referencias.get(url_name, [])) > 0
        path_str = url_info['path']
        
        # Verificar se é API ou webhook
        is_api = 'api' in path_str.lower() or 'webhook' in path_str.lower()
        
        if url_name in urls_criticas:
            urls_utilizadas.append((url_name, url_info, 'Crítica'))
        elif not view_existe:
            urls_nao_utilizadas.append((url_name, url_info, 'View não existe'))
        elif is_api:
            urls_api_webhook.append((url_name, url_info, 'API/Webhook'))
        elif not tem_referencias:
            urls_nao_utilizadas.append((url_name, url_info, 'Sem referências'))
        else:
            ref_count = len(referencias[url_name])
            urls_utilizadas.append((url_name, url_info, f'{ref_count} referências'))
    
    # 5. Mostrar resultados
    print("\n" + "=" * 70)
    print("RESULTADOS DA ANALISE")
    print("=" * 70)
    
    print(f"\nURLs Utilizadas: {len(urls_utilizadas)}")
    print(f"URLs API/Webhook: {len(urls_api_webhook)}")
    print(f"URLs Nao Utilizadas: {len(urls_nao_utilizadas)}")
    
    if urls_nao_utilizadas:
        print("\n" + "-" * 70)
        print("URLs NAO UTILIZADAS (candidatas para remocao):")
        print("-" * 70)
        for url_name, url_info, motivo in urls_nao_utilizadas[:30]:  # Mostrar primeiras 30
            print(f"\n  {url_name}")
            print(f"    Path: {url_info['path']}")
            print(f"    View: {url_info['view']}")
            print(f"    Motivo: {motivo}")
    
    # 6. Salvar relatório
    relatorio_file = Path(settings.BASE_DIR) / 'relatorio_urls_nao_utilizadas.txt'
    with open(relatorio_file, 'w', encoding='utf-8') as f:
        f.write("RELATORIO DE URLs NAO UTILIZADAS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total de URLs analisadas: {len(todas_urls)}\n")
        f.write(f"URLs utilizadas: {len(urls_utilizadas)}\n")
        f.write(f"URLs API/Webhook: {len(urls_api_webhook)}\n")
        f.write(f"URLs nao utilizadas: {len(urls_nao_utilizadas)}\n\n")
        
        f.write("\nURLs NAO UTILIZADAS:\n")
        f.write("-" * 70 + "\n")
        for url_name, url_info, motivo in urls_nao_utilizadas:
            f.write(f"\n{url_name}\n")
            f.write(f"  Path: {url_info['path']}\n")
            f.write(f"  View: {url_info['view']}\n")
            f.write(f"  Motivo: {motivo}\n")
    
    print(f"\nRelatorio salvo em: {relatorio_file}")
    
    return urls_nao_utilizadas

if __name__ == '__main__':
    urls_nao_utilizadas = main()
    print(f"\nTotal de URLs nao utilizadas encontradas: {len(urls_nao_utilizadas)}")






