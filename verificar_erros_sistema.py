#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar erros no sistema:
- Templates faltantes
- URLs incorretas
- Views faltantes
- Imports incorretos
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / 'templates' / 'gestao_rural'
GESTAO_RURAL = BASE_DIR / 'gestao_rural'

ERROS_ENCONTRADOS = []
AVISOS = []

def verificar_template_existe(template_path):
    """Verifica se template existe"""
    # Converter 'gestao_rural/template.html' para path relativo
    if template_path.startswith('gestao_rural/'):
        template_path = template_path.replace('gestao_rural/', '')
    
    template_file = TEMPLATES_DIR / template_path
    return template_file.exists()

def verificar_view_existe(view_name, arquivo='views.py'):
    """Verifica se view existe"""
    view_file = GESTAO_RURAL / arquivo
    if not view_file.exists():
        return False
    
    try:
        with open(view_file, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            # Procurar por definição da função
            pattern = rf'def\s+{view_name}\s*\('
            return bool(re.search(pattern, conteudo))
    except:
        return False

def verificar_url_existe(url_name, arquivo='urls.py'):
    """Verifica se URL existe"""
    url_file = GESTAO_RURAL / arquivo
    if not url_file.exists():
        return False
    
    try:
        with open(url_file, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            # Procurar por name='url_name'
            pattern = rf"name=['\"]{url_name}['\"]"
            return bool(re.search(pattern, conteudo))
    except:
        return False

def verificar_views():
    """Verifica views e seus templates"""
    print("=== VERIFICANDO VIEWS E TEMPLATES ===\n")
    
    for view_file in GESTAO_RURAL.glob('views*.py'):
        print(f"Verificando {view_file.name}...")
        
        try:
            with open(view_file, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
                
            for i, linha in enumerate(linhas, 1):
                # Procurar por render()
                match = re.search(r"render\s*\(\s*request\s*,\s*['\"]([^'\"]+)['\"]", linha)
                if match:
                    template = match.group(1)
                    
                    if not verificar_template_existe(template):
                        ERROS_ENCONTRADOS.append({
                            'tipo': 'TEMPLATE_FALTANTE',
                            'arquivo': str(view_file.relative_to(BASE_DIR)),
                            'linha': i,
                            'template': template,
                            'descricao': f'Template não encontrado: {template}'
                        })
                        
        except Exception as e:
            ERROS_ENCONTRADOS.append({
                'tipo': 'ERRO_LEITURA',
                'arquivo': str(view_file.relative_to(BASE_DIR)),
                'linha': 0,
                'descricao': f'Erro ao ler arquivo: {e}'
            })

def verificar_templates_urls():
    """Verifica URLs usadas nos templates"""
    print("\n=== VERIFICANDO URLs NOS TEMPLATES ===\n")
    
    for template_file in TEMPLATES_DIR.rglob('*.html'):
        if '__pycache__' not in str(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    linhas = conteudo.split('\n')
                
                # Procurar por {% url 'nome' %}
                for i, linha in enumerate(linhas, 1):
                    matches = re.findall(r"url\s+['\"]([^'\"]+)['\"]", linha)
                    for url_name in matches:
                        # Ignorar URLs do Django admin
                        if url_name.startswith('admin:'):
                            continue
                        
                        # Verificar se URL existe
                        if not verificar_url_existe(url_name):
                            # Verificar em todos os arquivos urls*.py
                            encontrado = False
                            for url_file in GESTAO_RURAL.glob('urls*.py'):
                                if verificar_url_existe(url_name, url_file.name):
                                    encontrado = True
                                    break
                            
                            if not encontrado:
                                AVISOS.append({
                                    'tipo': 'URL_INEXISTENTE',
                                    'arquivo': str(template_file.relative_to(BASE_DIR)),
                                    'linha': i,
                                    'url': url_name,
                                    'descricao': f'URL não encontrada: {url_name}'
                                })
            except Exception as e:
                ERROS_ENCONTRADOS.append({
                    'tipo': 'ERRO_LEITURA_TEMPLATE',
                    'arquivo': str(template_file.relative_to(BASE_DIR)),
                    'linha': 0,
                    'descricao': f'Erro ao ler template: {e}'
                })

def verificar_imports():
    """Verifica imports incorretos"""
    print("\n=== VERIFICANDO IMPORTS ===\n")
    
    for py_file in GESTAO_RURAL.rglob('*.py'):
        if py_file.name.startswith('__'):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                linhas = conteudo.split('\n')
            
            for i, linha in enumerate(linhas, 1):
                # Procurar imports de views
                match = re.search(r'from\s+\.\s+import\s+views_(\w+)', linha)
                if match:
                    mod_name = match.group(1)
                    mod_file = GESTAO_RURAL / f'views_{mod_name}.py'
                    
                    if not mod_file.exists():
                        ERROS_ENCONTRADOS.append({
                            'tipo': 'IMPORT_INCORRETO',
                            'arquivo': str(py_file.relative_to(BASE_DIR)),
                            'linha': i,
                            'descricao': f'Módulo não encontrado: views_{mod_name}.py'
                        })
        except:
            pass

def main():
    """Função principal"""
    print("🔍 VERIFICANDO ERROS NO SISTEMA...\n")
    
    verificar_views()
    verificar_templates_urls()
    verificar_imports()
    
    # Agrupar por tipo
    erros_por_tipo = {}
    for erro in ERROS_ENCONTRADOS:
        tipo = erro['tipo']
        if tipo not in erros_por_tipo:
            erros_por_tipo[tipo] = []
        erros_por_tipo[tipo].append(erro)
    
    avisos_por_tipo = {}
    for aviso in AVISOS:
        tipo = aviso['tipo']
        if tipo not in avisos_por_tipo:
            avisos_por_tipo[tipo] = []
        avisos_por_tipo[tipo].append(aviso)
    
    print(f"\n{'='*60}")
    print(f"TOTAL DE ERROS: {len(ERROS_ENCONTRADOS)}")
    print(f"TOTAL DE AVISOS: {len(AVISOS)}")
    print(f"{'='*60}\n")
    
    if erros_por_tipo:
        print("❌ ERROS ENCONTRADOS:\n")
        for tipo, erros in erros_por_tipo.items():
            print(f"[{tipo}]: {len(erros)} problemas")
            for e in erros[:5]:
                print(f"  - {e['arquivo']}:{e['linha']} - {e['descricao']}")
            if len(erros) > 5:
                print(f"  ... e mais {len(erros) - 5} problemas")
            print()
    
    if avisos_por_tipo:
        print("⚠️ AVISOS:\n")
        for tipo, avisos in avisos_por_tipo.items():
            print(f"[{tipo}]: {len(avisos)} avisos")
            for a in avisos[:5]:
                print(f"  - {a['arquivo']}:{a['linha']} - {a['descricao']}")
            if len(avisos) > 5:
                print(f"  ... e mais {len(avisos) - 5} avisos")
            print()
    
    # Salvar relatório
    relatorio = BASE_DIR / 'RELATORIO_ERROS_SISTEMA.txt'
    with open(relatorio, 'w', encoding='utf-8') as f:
        f.write("=== RELATÓRIO DE ERROS DO SISTEMA ===\n\n")
        
        if erros_por_tipo:
            f.write("ERROS ENCONTRADOS:\n\n")
            for tipo, erros in erros_por_tipo.items():
                f.write(f"[{tipo}] - {len(erros)} problemas:\n")
                for e in erros:
                    f.write(f"  {e['arquivo']}:{e['linha']} - {e['descricao']}\n")
                f.write("\n")
        
        if avisos_por_tipo:
            f.write("AVISOS:\n\n")
            for tipo, avisos in avisos_por_tipo.items():
                f.write(f"[{tipo}] - {len(avisos)} avisos:\n")
                for a in avisos:
                    f.write(f"  {a['arquivo']}:{a['linha']} - {a['descricao']}\n")
                f.write("\n")
    
    print(f"✅ Relatório salvo em: {relatorio}")

if __name__ == '__main__':
    main()



