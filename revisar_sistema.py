#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Revisão Completa do Sistema Monpec
Verifica e corrige problemas comuns no código
"""

import os
import re
import ast
import sys
from pathlib import Path

# Configurações
BASE_DIR = Path(__file__).parent
GESTAO_RURAL_DIR = BASE_DIR / 'gestao_rural'
TEMPLATES_DIR = BASE_DIR / 'templates'

PROBLEMAS_ENCONTRADOS = []
CORRECOES_APLICADAS = []


def log_problema(arquivo, linha, tipo, descricao, correcao=None):
    """Registra um problema encontrado"""
    problema = {
        'arquivo': str(arquivo),
        'linha': linha,
        'tipo': tipo,
        'descricao': descricao,
        'correcao': correcao
    }
    PROBLEMAS_ENCONTRADOS.append(problema)
    print(f"⚠️  [{tipo}] {arquivo}:{linha} - {descricao}")


def log_correcao(arquivo, linha, descricao):
    """Registra uma correção aplicada"""
    correcao = {
        'arquivo': str(arquivo),
        'linha': linha,
        'descricao': descricao
    }
    CORRECOES_APLICADAS.append(correcao)
    print(f"✅ CORRIGIDO: {arquivo}:{linha} - {descricao}")


def verificar_imports_python(arquivo):
    """Verifica problemas de imports em arquivos Python"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            linhas = conteudo.split('\n')
            
        # Verificar imports faltando
        if 'JsonResponse' in conteudo and 'from django.http import JsonResponse' not in conteudo:
            # Verificar se está importado de outra forma
            if 'JsonResponse' not in [imp.split('import')[1].strip() if 'import' in imp else '' for imp in conteudo.split('\n') if imp.strip().startswith('from django.http')]:
                log_problema(arquivo, 0, 'IMPORT', 'JsonResponse pode estar faltando', 'Adicionar: from django.http import JsonResponse')
        
        # Verificar decorators faltando
        view_funcs = re.findall(r'^def (\w+)\(request', conteudo, re.MULTILINE)
        for func_name in view_funcs:
            if func_name not in ['login_view']:  # login_view não precisa de @login_required
                # Procurar a linha da função
                for i, linha in enumerate(linhas, 1):
                    if re.match(rf'^def {func_name}\(', linha):
                        # Verificar se tem @login_required acima
                        if i > 1 and '@login_required' not in linhas[i-2]:
                            # Verificar se não está em uma lista de exceções
                            if 'pecuaria_inventario_dados' not in func_name:
                                log_problema(arquivo, i, 'DECORATOR', f'View {func_name} pode precisar de @login_required')
                        break
        
    except SyntaxError as e:
        log_problema(arquivo, 0, 'SYNTAX', f'Erro de sintaxe: {e}')
    except Exception as e:
        log_problema(arquivo, 0, 'ERRO', f'Erro ao verificar arquivo: {e}')


def verificar_templates_html(arquivo):
    """Verifica problemas em templates HTML"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            linhas = conteudo.split('\n')
        
        # Verificar tags não fechadas
        tags_abertas = {}
        for i, linha in enumerate(linhas, 1):
            # Verificar {% if %} sem {% endif %}
            if '{% if' in linha and '{% endif %}' not in linha:
                tag = re.search(r'{% if\s+([^%]+)%}', linha)
                if tag:
                    tag_key = f"if_{i}"
                    tags_abertas[tag_key] = {'tipo': 'if', 'linha': i}
            elif '{% endif %}' in linha:
                if tags_abertas:
                    tags_abertas.popitem()
            
            # Verificar {% for %} sem {% endfor %}
            if '{% for' in linha and '{% endfor %}' not in linha:
                tag = re.search(r'{% for\s+([^%]+)%}', linha)
                if tag:
                    tag_key = f"for_{i}"
                    tags_abertas[tag_key] = {'tipo': 'for', 'linha': i}
            elif '{% endfor %}' in linha:
                if tags_abertas:
                    for key in list(tags_abertas.keys()):
                        if tags_abertas[key]['tipo'] == 'for':
                            tags_abertas.pop(key)
                            break
        
        if tags_abertas:
            for tag_info in tags_abertas.values():
                log_problema(arquivo, tag_info['linha'], 'TEMPLATE', f"Tag {tag_info['tipo']} pode não estar fechada")
        
        # Verificar extends faltando
        if '{% extends' not in conteudo and 'pecuaria_parametros.html' not in str(arquivo):
            # Pode ser um template parcial, então só avisar se tiver blocos
            if '{% block' in conteudo:
                log_problema(arquivo, 0, 'TEMPLATE', 'Template tem blocos mas não tem {% extends %}', 'Verificar se é template parcial')
        
    except Exception as e:
        log_problema(arquivo, 0, 'ERRO', f'Erro ao verificar template: {e}')


def verificar_javascript(arquivo):
    """Verifica problemas em JavaScript"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verificar console.log em produção (opcional, apenas avisar)
        console_logs = len(re.findall(r'console\.(log|warn|error)', conteudo))
        if console_logs > 20:
            log_problema(arquivo, 0, 'JAVASCRIPT', f'Muitos console.log encontrados ({console_logs}). Considerar remover em produção.')
        
        # Verificar funções não fechadas
        if 'function' in conteudo:
            funcoes = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s*\{', conteudo)
            for func_name in funcoes:
                # Tentar encontrar o fechamento
                pattern = rf'function\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{'
                match = re.search(pattern, conteudo)
                if match:
                    # Verificar se há fechamento correspondente
                    pos_inicio = match.end()
                    brace_count = 1
                    pos = pos_inicio
                    while pos < len(conteudo) and brace_count > 0:
                        if conteudo[pos] == '{':
                            brace_count += 1
                        elif conteudo[pos] == '}':
                            brace_count -= 1
                        pos += 1
                    if brace_count > 0:
                        log_problema(arquivo, conteudo[:match.start()].count('\n') + 1, 'JAVASCRIPT', f'Função {func_name} pode não estar fechada corretamente')
        
    except Exception as e:
        log_problema(arquivo, 0, 'ERRO', f'Erro ao verificar JavaScript: {e}')


def revisar_arquivos():
    """Revisa todos os arquivos do sistema"""
    print("=== REVISÃO COMPLETA DO SISTEMA ===\n")
    
    # Revisar arquivos Python
    print("📁 Revisando arquivos Python...")
    for arquivo_py in GESTAO_RURAL_DIR.rglob('*.py'):
        if '__pycache__' not in str(arquivo_py):
            verificar_imports_python(arquivo_py)
    
    # Revisar templates HTML
    print("\n📁 Revisando templates HTML...")
    for arquivo_html in TEMPLATES_DIR.rglob('*.html'):
        verificar_templates_html(arquivo_html)
        # Verificar JavaScript inline
        try:
            with open(arquivo_html, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                if '<script>' in conteudo:
                    verificar_javascript(arquivo_html)
        except:
            pass
    
    # Gerar relatório
    print("\n" + "="*60)
    print(f"TOTAL DE PROBLEMAS ENCONTRADOS: {len(PROBLEMAS_ENCONTRADOS)}")
    print("="*60)
    
    # Agrupar por tipo
    por_tipo = {}
    for problema in PROBLEMAS_ENCONTRADOS:
        tipo = problema['tipo']
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(problema)
    
    for tipo, problemas in por_tipo.items():
        print(f"\n[{tipo}]: {len(problemas)} problemas")
        for p in problemas[:5]:  # Mostrar apenas os 5 primeiros de cada tipo
            print(f"  - {Path(p['arquivo']).name}:{p['linha']} - {p['descricao']}")
        if len(problemas) > 5:
            print(f"  ... e mais {len(problemas) - 5} problemas")
    
    # Salvar relatório
    relatorio = BASE_DIR / 'RELATORIO_REVISAO.txt'
    with open(relatorio, 'w', encoding='utf-8') as f:
        f.write("=== RELATÓRIO DE REVISÃO DO SISTEMA ===\n\n")
        f.write(f"Total de problemas encontrados: {len(PROBLEMAS_ENCONTRADOS)}\n\n")
        for tipo, problemas in por_tipo.items():
            f.write(f"\n[{tipo}] - {len(problemas)} problemas:\n")
            for p in problemas:
                f.write(f"  {p['arquivo']}:{p['linha']} - {p['descricao']}\n")
                if p['correcao']:
                    f.write(f"    Sugestão: {p['correcao']}\n")
    
    print(f"\n✅ Relatório salvo em: {relatorio}")


if __name__ == '__main__':
    revisar_arquivos()

















