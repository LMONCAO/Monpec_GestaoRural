#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analise profunda modulo por modulo - verificando views, templates, models
"""

import os
import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
GESTAO_RURAL = BASE_DIR / 'gestao_rural'
TEMPLATES_DIR = BASE_DIR / 'templates' / 'gestao_rural'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

PROBLEMAS = []
TEMPLATES_FALTANTES = []
VIEWS_PROBLEMAS = []

def analisar_view_e_template(arquivo_view, funcao_view):
    """Analisa uma view e verifica se o template existe"""
    try:
        with open(arquivo_view, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Procurar a funcao
        pattern = rf'def\s+{funcao_view}\s*\([^)]*\):.*?return\s+(render|redirect|JsonResponse|HttpResponse)'
        match = re.search(pattern, conteudo, re.DOTALL)
        
        if not match:
            VIEWS_PROBLEMAS.append({
                'arquivo': str(arquivo_view),
                'funcao': funcao_view,
                'problema': 'Nao encontrou return render/redirect'
            })
            return
        
        # Procurar template no render
        template_match = re.search(r'render\s*\(\s*request\s*,\s*[\'"]([^\'"]+)[\'"]', conteudo, re.DOTALL)
        if template_match:
            template_name = template_match.group(1)
            
            # Verificar se template existe
            template_paths = [
                TEMPLATES_DIR / template_name,
                BASE_DIR / 'templates' / template_name,
            ]
            
            existe = any(p.exists() for p in template_paths)
            if not existe:
                TEMPLATES_FALTANTES.append({
                    'arquivo': str(arquivo_view),
                    'funcao': funcao_view,
                    'template': template_name
                })
    
    except Exception as e:
        PROBLEMAS.append({
            'arquivo': str(arquivo_view),
            'funcao': funcao_view,
            'erro': str(e)
        })

def analisar_arquivo_completo(arquivo):
    """Analisa arquivo de views completo"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            linhas = conteudo.split('\n')
        
        # Encontrar todas as funcoes de view
        views_encontradas = []
        for i, linha in enumerate(linhas):
            match = re.match(r'^def\s+(\w+)\(request', linha)
            if match:
                funcao = match.group(1)
                views_encontradas.append((funcao, i+1))
        
        # Analisar cada view
        for funcao, linha in views_encontradas:
            analisar_view_e_template(arquivo, funcao)
    
    except Exception as e:
        print(f"[ERRO] Erro ao analisar {arquivo}: {e}")

def verificar_imports_modelos(arquivo):
    """Verifica se os modelos importados existem"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Procurar imports de models
        imports_models = re.findall(r'from\s+\.models(?:_\w+)?\s+import\s+([^#\n]+)', conteudo)
        
        for import_line in imports_models:
            modelos = [m.strip() for m in import_line.split(',')]
            # Aqui poderia verificar se cada modelo existe nos arquivos models
            # Por ora apenas registramos
            pass
    
    except Exception as e:
        pass

def analisar_modulo(modulo_nome, arquivos_views):
    """Analisa um modulo completo"""
    print(f"\n{'='*80}")
    print(f"  MODULO: {modulo_nome}")
    print(f"{'='*80}\n")
    
    for arquivo_nome in arquivos_views:
        arquivo = GESTAO_RURAL / arquivo_nome
        if arquivo.exists():
            print(f"[*] Analisando {arquivo_nome}...")
            analisar_arquivo_completo(arquivo)
            verificar_imports_modelos(arquivo)
        else:
            print(f"[!] Arquivo nao encontrado: {arquivo_nome}")

def main():
    """Funcao principal"""
    print("\n" + "="*80)
    print("  ANALISE PROFUNDA - MODULO POR MODULO")
    print("="*80)
    
    # Definir modulos e seus arquivos
    modulos = {
        'PECUARIA': [
            'views_pecuaria_completa.py',
            'views.py',  # Contem views de pecuaria tambem
        ],
        'CURRAL/V3': [
            'views_curral.py',
        ],
        'FINANCEIRO': [
            'views_financeiro.py',
            'views_financeiro_avancado.py',
        ],
        'RASTREABILIDADE': [
            'views_rastreabilidade.py',
            'views_relatorios_rastreabilidade.py',
        ],
        'COMPRAS': [
            'views_compras.py',
        ],
        'CUSTOS': [
            'views_custos.py',
        ],
        'VENDAS': [
            'views_vendas.py',
        ],
        'IATF': [
            'views_iatf_completo.py',
        ],
        'IMOBILIZADO': [
            'views_imobilizado.py',
        ],
        'NUTRICAO': [
            'views_nutricao.py',
        ],
        'OPERACOES': [
            'views_operacoes.py',
        ],
        'FUNCIONARIOS': [
            'views_funcionarios.py',
        ],
    }
    
    # Analisar cada modulo
    for modulo_nome, arquivos in modulos.items():
        analisar_modulo(modulo_nome, arquivos)
    
    # Relatorio final
    print(f"\n{'='*80}")
    print("  RELATORIO FINAL")
    print(f"{'='*80}\n")
    
    print(f"Templates faltantes: {len(TEMPLATES_FALTANTES)}")
    if TEMPLATES_FALTANTES:
        print("\n=== TEMPLATES FALTANTES ===")
        for item in TEMPLATES_FALTANTES[:20]:  # Primeiros 20
            print(f"  - {item['arquivo']}:{item['funcao']} -> {item['template']}")
    
    print(f"\nViews com problemas: {len(VIEWS_PROBLEMAS)}")
    if VIEWS_PROBLEMAS:
        print("\n=== VIEWS COM PROBLEMAS ===")
        for item in VIEWS_PROBLEMAS[:20]:  # Primeiros 20
            print(f"  - {item['arquivo']}:{item['funcao']} -> {item['problema']}")
    
    print(f"\nTotal de problemas encontrados: {len(TEMPLATES_FALTANTES) + len(VIEWS_PROBLEMAS)}")

if __name__ == '__main__':
    main()

