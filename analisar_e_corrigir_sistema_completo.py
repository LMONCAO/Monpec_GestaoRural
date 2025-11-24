#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script completo para analisar e corrigir TODOS os erros do sistema
Analisa modulo por modulo e tela por tela
"""

import os
import sys
import subprocess
import re
import ast
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent
GESTAO_RURAL = BASE_DIR / 'gestao_rural'
TEMPLATES_DIR = BASE_DIR / 'templates' / 'gestao_rural'

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

ERROS_ENCONTRADOS = []
CORRECOES_REALIZADAS = []

def print_header(msg):
    """Imprime cabecalho formatado"""
    print("\n" + "=" * 80)
    print(f"  {msg}")
    print("=" * 80 + "\n")

def log_erro(arquivo, linha, tipo, descricao, correcao=None):
    """Registra erro encontrado"""
    ERROS_ENCONTRADOS.append({
        'arquivo': str(arquivo),
        'linha': linha,
        'tipo': tipo,
        'descricao': descricao,
        'correcao': correcao
    })
    print(f"[ERRO] {arquivo.name}:{linha} - {tipo}: {descricao}")

def log_correcao(arquivo, linha, descricao):
    """Registra correcao realizada"""
    CORRECOES_REALIZADAS.append({
        'arquivo': str(arquivo),
        'linha': linha,
        'descricao': descricao
    })
    print(f"[OK] Corrigido: {arquivo.name}:{linha} - {descricao}")

def verificar_sintaxe_python(arquivo):
    """Verifica sintaxe Python de um arquivo"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        ast.parse(codigo, filename=str(arquivo))
        return True, None
    except SyntaxError as e:
        return False, f"Erro de sintaxe na linha {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Erro ao analisar: {str(e)}"

def verificar_imports_faltantes(arquivo):
    """Verifica e corrige imports faltantes"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            linhas = conteudo.split('\n')
        
        conteudo_original = conteudo
        modificado = False
        
        # Verificar JsonResponse
        if 'JsonResponse' in conteudo and 'from django.http import JsonResponse' not in conteudo:
            if 'from django.http import' in conteudo:
                # Adicionar JsonResponse ao import existente
                conteudo = re.sub(
                    r'(from django\.http import)([^\n]+)',
                    lambda m: f"{m.group(1)}{m.group(2)}, JsonResponse" if 'JsonResponse' not in m.group(2) else m.group(0),
                    conteudo
                )
            else:
                # Adicionar novo import apos outros imports django
                padrao = r'(from django\.[^\n]+\n)'
                match = re.search(padrao, conteudo)
                if match:
                    pos = match.end()
                    conteudo = conteudo[:pos] + 'from django.http import JsonResponse\n' + conteudo[pos:]
                else:
                    # Adicionar no inicio
                    linhas.insert(0, 'from django.http import JsonResponse')
                    conteudo = '\n'.join(linhas)
            
            if conteudo != conteudo_original:
                modificado = True
                log_correcao(arquivo, 0, "Import JsonResponse adicionado")
        
        if modificado:
            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            return True
        
        return False
    except Exception as e:
        log_erro(arquivo, 0, 'IMPORT', f"Erro ao verificar imports: {e}")
        return False

def verificar_template_existe(template_name, views_file):
    """Verifica se template existe"""
    template_path = TEMPLATES_DIR / template_name
    if not template_path.exists():
        # Tentar variações
        template_path_alt = BASE_DIR / 'templates' / template_name
        if not template_path_alt.exists():
            log_erro(views_file, 0, 'TEMPLATE', f"Template nao encontrado: {template_name}")
            return False
    return True

def analisar_view_function(func_name, func_code, arquivo, linha_inicio):
    """Analisa uma funcao de view"""
    problemas = []
    
    # Verificar se tem decorator @login_required (exceto login_view)
    if 'def ' + func_name + '(' in func_code:
        if func_name not in ['login_view', 'landing_page', 'google_search_console_verification']:
            if '@login_required' not in func_code:
                problemas.append({
                    'linha': linha_inicio,
                    'tipo': 'DECORATOR',
                    'descricao': f"View {func_name} pode precisar de @login_required"
                })
    
    # Verificar se retorna render ou redirect
    if 'return render(' not in func_code and 'return redirect(' not in func_code and 'return JsonResponse(' not in func_code and 'return HttpResponse(' not in func_code:
        if 'def ' + func_name in func_code:
            problemas.append({
                'linha': linha_inicio,
                'tipo': 'RETURN',
                'descricao': f"View {func_name} pode nao estar retornando resposta adequada"
            })
    
    return problemas

def analisar_arquivo_views(arquivo):
    """Analisa um arquivo de views"""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            linhas = conteudo.split('\n')
        
        problemas = []
        
        # Verificar sintaxe
        ok, erro = verificar_sintaxe_python(arquivo)
        if not ok:
            log_erro(arquivo, 0, 'SYNTAX', erro)
            return
        
        # Verificar imports
        verificar_imports_faltantes(arquivo)
        
        # Encontrar funcoes de view
        for i, linha in enumerate(linhas, 1):
            match = re.match(r'^def (\w+)\(request', linha)
            if match:
                func_name = match.group(1)
                # Obter codigo da funcao (aproximado)
                func_code = ''
                j = i - 1
                while j < len(linhas) and (j == i - 1 or linhas[j].startswith(' ') or linhas[j].startswith('\t')):
                    func_code += linhas[j] + '\n'
                    j += 1
                
                problemas_func = analisar_view_function(func_name, func_code, arquivo, i)
                problemas.extend(problemas_func)
        
        # Verificar templates usados
        templates = re.findall(r"render\(request,\s*['\"]([^'\"]+)['\"]", conteudo)
        for template in templates:
            verificar_template_existe(template, arquivo)
        
        return problemas
    except Exception as e:
        log_erro(arquivo, 0, 'ANALISE', f"Erro ao analisar arquivo: {e}")

def analisar_modulo_pecuaria():
    """Analisa modulo Pecuaria"""
    print_header("MODULO: PECUARIA")
    
    arquivos = [
        'views_pecuaria_completa.py',
        'models.py',  # Contem models de pecuaria
        'views.py',  # Contem algumas views de pecuaria
    ]
    
    for arquivo_nome in arquivos:
        arquivo = GESTAO_RURAL / arquivo_nome
        if arquivo.exists():
            print(f"\n[*] Analisando {arquivo_nome}...")
            analisar_arquivo_views(arquivo)
        else:
            print(f"[!] Arquivo nao encontrado: {arquivo_nome}")

def analisar_modulo_curral():
    """Analisa modulo Curral"""
    print_header("MODULO: CURRAL/V3")
    
    arquivo = GESTAO_RURAL / 'views_curral.py'
    if arquivo.exists():
        print(f"\n[*] Analisando views_curral.py...")
        analisar_arquivo_views(arquivo)
    else:
        print("[!] Arquivo views_curral.py nao encontrado")

def analisar_modulo_financeiro():
    """Analisa modulo Financeiro"""
    print_header("MODULO: FINANCEIRO")
    
    arquivos = [
        'views_financeiro.py',
        'views_financeiro_avancado.py',
        'models_financeiro.py',
    ]
    
    for arquivo_nome in arquivos:
        arquivo = GESTAO_RURAL / arquivo_nome
        if arquivo.exists():
            print(f"\n[*] Analisando {arquivo_nome}...")
            analisar_arquivo_views(arquivo)
        else:
            print(f"[!] Arquivo nao encontrado: {arquivo_nome}")

def analisar_modulo_rastreabilidade():
    """Analisa modulo Rastreabilidade"""
    print_header("MODULO: RASTREABILIDADE")
    
    arquivo = GESTAO_RURAL / 'views_rastreabilidade.py'
    if arquivo.exists():
        print(f"\n[*] Analisando views_rastreabilidade.py...")
        analisar_arquivo_views(arquivo)
    else:
        print("[!] Arquivo views_rastreabilidade.py nao encontrado")

def analisar_modulo_compras():
    """Analisa modulo Compras"""
    print_header("MODULO: COMPRAS")
    
    arquivo = GESTAO_RURAL / 'views_compras.py'
    if arquivo.exists():
        print(f"\n[*] Analisando views_compras.py...")
        analisar_arquivo_views(arquivo)
    else:
        print("[!] Arquivo views_compras.py nao encontrado")

def analisar_todos_modulos():
    """Analisa todos os modulos do sistema"""
    print_header("INICIANDO ANALISE COMPLETA DO SISTEMA")
    
    modulos = [
        ('Pecuaria', analisar_modulo_pecuaria),
        ('Curral/V3', analisar_modulo_curral),
        ('Financeiro', analisar_modulo_financeiro),
        ('Rastreabilidade', analisar_modulo_rastreabilidade),
        ('Compras', analisar_modulo_compras),
    ]
    
    for nome_modulo, funcao_analise in modulos:
        try:
            funcao_analise()
        except Exception as e:
            print(f"[ERRO] Erro ao analisar modulo {nome_modulo}: {e}")

def gerar_relatorio():
    """Gera relatorio final"""
    print_header("RELATORIO FINAL")
    
    print(f"\nTotal de erros encontrados: {len(ERROS_ENCONTRADOS)}")
    print(f"Total de correcoes realizadas: {len(CORRECOES_REALIZADAS)}")
    
    if ERROS_ENCONTRADOS:
        print("\n=== ERROS ENCONTRADOS ===")
        por_tipo = defaultdict(list)
        for erro in ERROS_ENCONTRADOS:
            por_tipo[erro['tipo']].append(erro)
        
        for tipo, erros in por_tipo.items():
            print(f"\n{tipo}: {len(erros)} erro(s)")
            for erro in erros[:5]:  # Mostrar apenas os primeiros 5
                print(f"  - {erro['arquivo']}:{erro['linha']} - {erro['descricao']}")
    
    if CORRECOES_REALIZADAS:
        print("\n=== CORRECOES REALIZADAS ===")
        for correcao in CORRECOES_REALIZADAS[:10]:  # Mostrar apenas as primeiras 10
            print(f"  [OK] {correcao['arquivo']} - {correcao['descricao']}")

def main():
    """Funcao principal"""
    print("\n" + "=" * 80)
    print("  ANALISE E CORRECAO COMPLETA DO SISTEMA")
    print("  Analisando modulo por modulo e tela por tela")
    print("=" * 80)
    
    # Analisar todos os modulos
    analisar_todos_modulos()
    
    # Verificacao final com Django
    print_header("VERIFICACAO FINAL COM DJANGO")
    try:
        result = subprocess.run(
            ['python', 'manage.py', 'check'],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            print("[OK] Django check passou sem erros!")
        else:
            print("[!] Django check encontrou problemas:")
            print(result.stdout[:500])
    except Exception as e:
        print(f"[ERRO] Erro ao executar Django check: {e}")
    
    # Gerar relatorio
    gerar_relatorio()
    
    print("\n" + "=" * 80)
    print("  ANALISE CONCLUIDA")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    main()

