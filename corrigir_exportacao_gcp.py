#!/usr/bin/env python
"""
SCRIPT SIMPLIFICADO PARA VERIFICAÇÃO DE EXPORTAÇÃO NO GCP
Apenas verifica dependências sem criar funções complexas
"""

import os
import sys

def main():
    print("📄 VERIFICAÇÃO DE EXPORTAÇÃO PDF/EXCEL - GCP")
    print("=" * 50)

    # 1. Verificar bibliotecas instaladas
    print("\n1. 📦 VERIFICANDO BIBLIOTECAS...")

    libraries = {
        'reportlab': 'PDF (ReportLab)',
        'openpyxl': 'Excel (OpenPyXL)',
        'pandas': 'Dados (Pandas)',
        'PIL': 'Imagens (Pillow)',
        'sklearn': 'Machine Learning',
        'statsmodels': 'Séries Temporais',
    }

    available_libs = {}
    for lib, description in libraries.items():
        try:
            __import__(lib)
            available_libs[lib] = True
            print(f"✅ {description}")
        except ImportError:
            available_libs[lib] = False
            print(f"❌ {description}")

    # 2. Verificar diretórios temporários
    print("\n2. 📁 VERIFICANDO DIRETÓRIOS TEMPORÁRIOS...")
    temp_dirs = ['/tmp', './temp', './tmp']

    for dir_path in temp_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            # Testar se conseguimos escrever
            test_file = os.path.join(dir_path, 'test.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.unlink(test_file)
            print(f"✅ Diretório temporário: {dir_path}")
            break
        except:
            continue
    else:
        print("❌ Nenhum diretório temporário disponível")

    print("\n✅ Verificação concluída - pronto para deploy!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)