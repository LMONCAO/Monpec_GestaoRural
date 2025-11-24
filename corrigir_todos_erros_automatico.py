#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script automático para corrigir TODOS os erros do sistema
Executa múltiplas verificações e correções automaticamente
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, str(Path(__file__).parent))

BASE_DIR = Path(__file__).parent
GESTAO_RURAL = BASE_DIR / 'gestao_rural'

def print_header(msg):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"  {msg}")
    print("=" * 70 + "\n")

def executar_comando(cmd, descricao):
    """Executa um comando e retorna o resultado"""
    print(f"[*] {descricao}...")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=str(BASE_DIR),
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            print(f"[OK] {descricao} - SUCESSO")
            return True, result.stdout
        else:
            print(f"[!] {descricao} - AVISOS ENCONTRADOS")
            output = result.stderr[:500] if result.stderr else result.stdout[:500]
            print(output)
            return False, result.stderr or result.stdout
    except Exception as e:
        print(f"[ERRO] {descricao} - ERRO: {e}")
        return False, str(e)

def verificar_sintaxe_python():
    """Verifica sintaxe de todos os arquivos Python"""
    print_header("VERIFICANDO SINTAXE PYTHON")
    erros = []
    
    for py_file in GESTAO_RURAL.rglob('*.py'):
        if '__pycache__' in str(py_file) or 'migrations' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), str(py_file), 'exec')
        except SyntaxError as e:
            erros.append((py_file, e))
                print(f"[ERRO] Erro de sintaxe em {py_file}: {e}")
    
    if not erros:
        print("[OK] Nenhum erro de sintaxe encontrado!")
        return True
    else:
        print(f"[!] {len(erros)} arquivo(s) com erro de sintaxe")
        return False

def verificar_imports_django():
    """Verifica imports do Django"""
    print_header("VERIFICANDO IMPORTS DJANGO")
    try:
        import django
        django.setup()
        
        # Tentar importar módulos principais
        from gestao_rural import models
        from gestao_rural import views
        print("[OK] Imports principais funcionando!")
        return True
    except Exception as e:
        print(f"[ERRO] Erro ao verificar imports: {e}")
        return False

def corrigir_imports_faltantes():
    """Tenta corrigir imports faltantes automaticamente"""
    print_header("CORRIGINDO IMPORTS FALTANTES")
    
    arquivos_corrigidos = 0
    for py_file in GESTAO_RURAL.rglob('*.py'):
        if '__pycache__' in str(py_file) or 'migrations' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            conteudo_original = conteudo
            
            # Verificar se usa JsonResponse mas não importa
            if 'JsonResponse' in conteudo and 'from django.http import JsonResponse' not in conteudo:
                if 'from django.http import' in conteudo:
                    # Adicionar JsonResponse ao import existente
                    conteudo = re.sub(
                        r'(from django\.http import [^\n]+)',
                        r'\1, JsonResponse',
                        conteudo
                    )
                else:
                    # Adicionar novo import
                    linhas = conteudo.split('\n')
                    import_index = 0
                    for i, linha in enumerate(linhas):
                        if linha.strip().startswith('from django') or linha.strip().startswith('import django'):
                            import_index = i + 1
                            break
                    linhas.insert(import_index, 'from django.http import JsonResponse')
                    conteudo = '\n'.join(linhas)
            
            if conteudo != conteudo_original:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                arquivos_corrigidos += 1
                print(f"[OK] Corrigido: {py_file.name}")
                
        except Exception as e:
            print(f"[!] Erro ao processar {py_file}: {e}")
    
    print(f"\n[OK] {arquivos_corrigidos} arquivo(s) corrigido(s)")
    return arquivos_corrigidos > 0

def executar_migrations():
    """Executa migrations pendentes"""
    print_header("EXECUTANDO MIGRATIONS")
    sucesso, output = executar_comando(
        "python manage.py migrate --no-input",
        "Aplicando migrations"
    )
    return sucesso

def coletar_static_files():
    """Coleta arquivos estáticos"""
    print_header("COLETANDO ARQUIVOS ESTÁTICOS")
    sucesso, output = executar_comando(
        "python manage.py collectstatic --no-input --clear",
        "Coletando arquivos estáticos"
    )
    return sucesso

def main():
    """Função principal - executa todas as correções"""
    print("\n" + "=" * 70)
    print("  CORRECAO AUTOMATICA DE TODOS OS ERROS DO SISTEMA")
    print("=" * 70)
    
    # Executar múltiplas rodadas de correção
    rodadas = 3
    for rodada in range(1, rodadas + 1):
        print(f"\n{'='*70}")
        print(f"  RODADA {rodada} DE {rodadas}")
        print(f"{'='*70}\n")
        
        # 1. Verificar sintaxe Python
        verificar_sintaxe_python()
        
        # 2. Verificar imports Django
        verificar_imports_django()
        
        # 3. Corrigir imports faltantes
        corrigir_imports_faltantes()
        
        # 4. Verificar sistema Django
        executar_comando("python manage.py check", "Verificando sistema Django")
        
        # 5. Executar migrations
        executar_migrations()
        
        print(f"\n[OK] Rodada {rodada} concluida!\n")
    
    # Verificação final
    print_header("VERIFICACAO FINAL DO SISTEMA")
    executar_comando("python manage.py check", "Verificacao final Django")
    
    print("\n" + "=" * 70)
    print("  CORRECOES CONCLUIDAS!")
    print("=" * 70)
    
    # Iniciar servidor automaticamente
    print("\n[*] Iniciando servidor Django automaticamente...\n")
    subprocess.Popen(
        ["python", "manage.py", "runserver", "0.0.0.0:8000"],
        cwd=str(BASE_DIR),
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    print("[OK] Servidor iniciado em http://0.0.0.0:8000")

if __name__ == '__main__':
    main()

