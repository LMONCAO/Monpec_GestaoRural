#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para aplicar migrações pendentes do Django
Execute este script a partir da raiz do projeto
"""
import os
import sys
from pathlib import Path

# Detectar diretório raiz (dois níveis acima deste script)
SCRIPT_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPT_DIR.parent.parent

# Se não encontrar manage.py, tentar buscar recursivamente
if not (ROOT_DIR / "manage.py").exists():
    # Buscar manage.py a partir do diretório atual
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "manage.py").exists():
            ROOT_DIR = parent
            break

# Mudar para o diretório raiz
os.chdir(ROOT_DIR)

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(ROOT_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc

if __name__ == '__main__':
    print("=" * 70)
    print("APLICANDO MIGRAÇÕES PENDENTES")
    print("=" * 70)
    print(f"Diretório: {ROOT_DIR}")
    print()
    
    # Verificar migrações pendentes
    print("[1/3] Verificando migrações pendentes...")
    print()
    
    # Aplicar migrações
    print("[2/3] Aplicando migrações...")
    print()
    
    try:
        execute_from_command_line(['manage.py', 'migrate', 'gestao_rural', '--noinput'])
        print()
        print("[3/3] Verificando migrações aplicadas...")
        print()
        execute_from_command_line(['manage.py', 'showmigrations', 'gestao_rural'])
        print()
        print("=" * 70)
        print("[OK] MIGRAÇÕES APLICADAS COM SUCESSO!")
        print("=" * 70)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"[ERRO] Erro ao aplicar migrações: {e}")
        print("=" * 70)
        sys.exit(1)

