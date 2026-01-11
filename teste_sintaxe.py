#!/usr/bin/env python3
"""
Script para testar sintaxe de arquivos Python críticos
"""
import os
import sys
import ast

def test_syntax(file_path):
    """Testa se um arquivo Python tem sintaxe válida"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Tentar fazer parse da AST
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("🔍 TESTANDO SINTAXE DOS ARQUIVOS PYTHON CRÍTICOS")
    print("=" * 60)

    # Arquivos críticos para testar
    critical_files = [
        'gestao_rural/views.py',
        'gestao_rural/views_demo_setup.py',
        'gestao_rural/views_assinaturas.py',
        'sistema_rural/settings.py',
        'sistema_rural/settings_gcp.py',
        'sistema_rural/urls.py',
        'gestao_rural/urls.py',
    ]

    all_good = True

    for file_path in critical_files:
        if os.path.exists(file_path):
            ok, error = test_syntax(file_path)
            if ok:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path}: {error}")
                all_good = False
        else:
            print(f"⚠️  {file_path} - Arquivo não encontrado")

    print("\n" + "=" * 60)
    if all_good:
        print("🎉 TODOS OS ARQUIVOS TÊM SINTAXE CORRETA!")
    else:
        print("❌ ERROS DE SINTAXE ENCONTRADOS!")
        sys.exit(1)

if __name__ == '__main__':
    main()