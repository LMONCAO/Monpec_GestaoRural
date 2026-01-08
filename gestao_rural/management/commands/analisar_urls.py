# -*- coding: utf-8 -*-
"""
Comando para analisar todas as URLs do sistema e identificar URLs não utilizadas
"""

import os
import re
from pathlib import Path
from django.core.management.base import BaseCommand
from django.urls import get_resolver
from django.conf import settings

class Command(BaseCommand):
    help = 'Analisa todas as URLs do sistema e identifica URLs não utilizadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--remover',
            action='store_true',
            help='Remover URLs não utilizadas automaticamente',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 70)
        self.stdout.write('ANALISE DE URLs DO SISTEMA')
        self.stdout.write('=' * 70)
        
        # 1. Coletar todas as URLs do sistema
        resolver = get_resolver()
        todas_urls = self._coletar_urls(resolver)
        
        self.stdout.write(f'\nTotal de URLs encontradas: {len(todas_urls)}')
        
        # 2. Verificar quais views existem
        views_existentes = self._verificar_views_existentes(todas_urls)
        
        # 3. Verificar referências em templates e código
        referencias = self._buscar_referencias_urls(todas_urls)
        
        # 4. Identificar URLs não utilizadas
        urls_nao_utilizadas = []
        urls_utilizadas = []
        
        for url_name, url_info in todas_urls.items():
            # Verificar se a view existe
            view_existe = views_existentes.get(url_name, False)
            
            # Verificar se há referências
            tem_referencias = url_name in referencias or len(referencias.get(url_name, [])) > 0
            
            # URLs críticas que sempre devem existir
            urls_criticas = [
                'login', 'logout', 'dashboard', 'landing_page', 'admin',
                'health_check', 'sitemap', 'password_reset', 'password_reset_done',
                'password_reset_confirm', 'password_reset_complete',
            ]
            
            if url_name in urls_criticas:
                urls_utilizadas.append((url_name, url_info, 'Crítica'))
            elif not view_existe:
                urls_nao_utilizadas.append((url_name, url_info, 'View não existe'))
            elif not tem_referencias:
                # Verificar se é uma URL de API ou webhook (podem não ter referências diretas)
                if 'api' in url_info['path'].lower() or 'webhook' in url_info['path'].lower():
                    urls_utilizadas.append((url_name, url_info, 'API/Webhook'))
                else:
                    urls_nao_utilizadas.append((url_name, url_info, 'Sem referências'))
            else:
                urls_utilizadas.append((url_name, url_info, f'{len(referencias.get(url_name, []))} referências'))
        
        # 5. Mostrar resultados
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('URLs UTILIZADAS')
        self.stdout.write('=' * 70)
        self.stdout.write(f'Total: {len(urls_utilizadas)}')
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('URLs NAO UTILIZADAS')
        self.stdout.write('=' * 70)
        self.stdout.write(f'Total: {len(urls_nao_utilizadas)}')
        
        if urls_nao_utilizadas:
            for url_name, url_info, motivo in urls_nao_utilizadas:
                self.stdout.write(f'\n  - {url_name}')
                self.stdout.write(f'    Path: {url_info["path"]}')
                self.stdout.write(f'    View: {url_info.get("view", "N/A")}')
                self.stdout.write(f'    Motivo: {motivo}')
        
        # 6. Remover se solicitado
        if options['remover'] and urls_nao_utilizadas:
            self.stdout.write('\n' + '=' * 70)
            self.stdout.write('REMOÇÃO DE URLs NAO UTILIZADAS')
            self.stdout.write('=' * 70)
            self._remover_urls(urls_nao_utilizadas)
        
        return 0
    
    def _coletar_urls(self, resolver, prefix=''):
        """Coleta todas as URLs do sistema"""
        urls = {}
        
        for pattern in resolver.url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # É um include
                new_prefix = prefix + str(pattern.pattern)
                urls.update(self._coletar_urls(pattern, new_prefix))
            else:
                # É uma URL
                pattern_str = str(pattern.pattern)
                full_path = prefix + pattern_str
                
                if hasattr(pattern, 'name') and pattern.name:
                    view_name = 'N/A'
                    if hasattr(pattern, 'callback'):
                        if hasattr(pattern.callback, '__name__'):
                            view_name = pattern.callback.__name__
                        elif hasattr(pattern.callback, 'view_class'):
                            view_name = pattern.callback.view_class.__name__
                    
                    urls[pattern.name] = {
                        'path': full_path,
                        'view': view_name,
                        'pattern': pattern
                    }
        
        return urls
    
    def _verificar_views_existentes(self, todas_urls):
        """Verifica se as views referenciadas existem"""
        views_existentes = {}
        
        for url_name, url_info in todas_urls.items():
            view_name = url_info.get('view', '')
            if view_name == 'N/A':
                views_existentes[url_name] = True  # Assumir OK se não conseguir verificar
                continue
            
            # Tentar importar a view
            try:
                pattern = url_info['pattern']
                if hasattr(pattern, 'callback'):
                    views_existentes[url_name] = True
                else:
                    views_existentes[url_name] = False
            except:
                views_existentes[url_name] = False
        
        return views_existentes
    
    def _buscar_referencias_urls(self, todas_urls):
        """Busca referências a URLs em templates, código Python e JavaScript"""
        referencias = {url_name: [] for url_name in todas_urls.keys()}
        
        base_dir = Path(settings.BASE_DIR)
        
        # Buscar em templates HTML
        for template_file in base_dir.rglob('*.html'):
            try:
                content = template_file.read_text(encoding='utf-8')
                for url_name in todas_urls.keys():
                    # Buscar {% url 'nome' %}
                    if f"url '{url_name}'" in content or f'url "{url_name}"' in content:
                        referencias[url_name].append(str(template_file.relative_to(base_dir)))
                    # Buscar reverse('nome')
                    if f"reverse('{url_name}'" in content or f'reverse("{url_name}"' in content:
                        referencias[url_name].append(str(template_file.relative_to(base_dir)))
            except:
                pass
        
        # Buscar em código Python
        for py_file in base_dir.rglob('*.py'):
            if 'migrations' in str(py_file) or '__pycache__' in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding='utf-8')
                for url_name in todas_urls.keys():
                    # Buscar reverse('nome')
                    if f"reverse('{url_name}'" in content or f'reverse("{url_name}"' in content:
                        referencias[url_name].append(str(py_file.relative_to(base_dir)))
                    # Buscar redirect('nome')
                    if f"redirect('{url_name}'" in content or f'redirect("{url_name}"' in content:
                        referencias[url_name].append(str(py_file.relative_to(base_dir)))
                    # Buscar {% url 'nome' %} em strings
                    if f"url '{url_name}'" in content or f'url "{url_name}"' in content:
                        referencias[url_name].append(str(py_file.relative_to(base_dir)))
            except:
                pass
        
        # Buscar em JavaScript
        for js_file in base_dir.rglob('*.js'):
            try:
                content = js_file.read_text(encoding='utf-8')
                for url_name in todas_urls.keys():
                    # Buscar URLs em strings JavaScript
                    if f"/{todas_urls[url_name]['path']}" in content:
                        referencias[url_name].append(str(js_file.relative_to(base_dir)))
            except:
                pass
        
        return referencias
    
    def _remover_urls(self, urls_nao_utilizadas):
        """Remove URLs não utilizadas dos arquivos urls.py"""
        # Ler arquivo de URLs principal
        urls_file = Path(settings.BASE_DIR) / 'gestao_rural' / 'urls.py'
        
        if not urls_file.exists():
            self.stdout.write(self.style.ERROR(f'Arquivo não encontrado: {urls_file}'))
            return
        
        content = urls_file.read_text(encoding='utf-8')
        linhas_originais = content.split('\n')
        linhas_novas = []
        
        urls_para_remover = {url_info['path'] for _, url_info, _ in urls_nao_utilizadas}
        
        i = 0
        while i < len(linhas_originais):
            linha = linhas_originais[i]
            
            # Verificar se esta linha contém uma URL a ser removida
            remover_linha = False
            for url_path in urls_para_remover:
                if url_path in linha and 'path(' in linha:
                    remover_linha = True
                    break
            
            if not remover_linha:
                linhas_novas.append(linha)
            else:
                self.stdout.write(f'Removendo: {linha.strip()}')
            
            i += 1
        
        # Escrever arquivo atualizado
        novo_content = '\n'.join(linhas_novas)
        urls_file.write_text(novo_content, encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f'\nArquivo atualizado: {urls_file}'))






