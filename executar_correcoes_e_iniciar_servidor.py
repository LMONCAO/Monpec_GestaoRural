#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar correcoes multiplas e iniciar servidor automaticamente
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

def executar_comando(cmd):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            cmd.split(),
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def rodada_correcao(numero):
    """Executa uma rodada de verificacoes e correcoes"""
    print(f"\n{'='*70}")
    print(f"RODADA {numero} DE CORRECAO")
    print(f"{'='*70}\n")
    
    # 1. Verificar sistema Django
    print("[*] Verificando sistema Django...")
    sucesso, stdout, stderr = executar_comando("python manage.py check")
    if sucesso:
        print("[OK] Sistema Django OK")
    else:
        print(f"[!] Avisos encontrados: {stderr[:200]}")
    
    # 2. Verificar sintaxe Python
    print("[*] Verificando sintaxe Python...")
    arquivos = [
        "gestao_rural/views.py",
        "gestao_rural/views_curral.py",
        "gestao_rural/views_pecuaria_completa.py",
        "gestao_rural/urls.py"
    ]
    erros = 0
    for arquivo in arquivos:
        arquivo_path = BASE_DIR / arquivo
        if arquivo_path.exists():
            sucesso, stdout, stderr = executar_comando(f"python -m py_compile {arquivo}")
            if not sucesso:
                erros += 1
                print(f"[ERRO] {arquivo}: {stderr[:100]}")
    
    if erros == 0:
        print("[OK] Sintaxe Python OK")
    
    # 3. Verificar migrations
    print("[*] Verificando migrations...")
    sucesso, stdout, stderr = executar_comando("python manage.py migrate --check")
    if sucesso:
        print("[OK] Migrations OK")
    else:
        print("[*] Aplicando migrations...")
        executar_comando("python manage.py migrate --no-input")
    
    print(f"[OK] Rodada {numero} concluida!\n")

def main():
    """Funcao principal"""
    print("\n" + "="*70)
    print("CORRECAO AUTOMATICA DO SISTEMA")
    print("="*70)
    
    # Executar 3 rodadas de correcao
    for i in range(1, 4):
        rodada_correcao(i)
    
    # Verificacao final
    print("\n" + "="*70)
    print("VERIFICACAO FINAL")
    print("="*70 + "\n")
    
    sucesso, stdout, stderr = executar_comando("python manage.py check")
    if sucesso:
        print("[OK] Sistema verificado com sucesso!")
    else:
        print(f"[!] Avisos: {stderr[:300]}")
    
    # Iniciar servidor automaticamente
    print("\n" + "="*70)
    print("INICIANDO SERVIDOR AUTOMATICAMENTE")
    print("="*70 + "\n")
    print("[*] Servidor Django iniciando em http://0.0.0.0:8000")
    print("[*] Pressione Ctrl+C para parar o servidor\n")
    
    # Iniciar servidor
    os.system("python manage.py runserver 0.0.0.0:8000")

if __name__ == '__main__':
    main()

