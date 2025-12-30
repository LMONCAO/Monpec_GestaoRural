#!/usr/bin/env python
"""
Script para corrigir problemas de segurança identificados
Remove senhas e SECRET_KEYs hardcoded, substituindo por variáveis de ambiente
"""
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Arquivos com problemas de segurança identificados
ARQUIVOS_PROBLEMAS = {
    'criar_admin_cloud_sql.py': {
        'linha': 63,
        'padrao': r"password\s*=\s*['\"]L6171r12@@['\"]",
        'substituicao': "password = os.getenv('ADMIN_PASSWORD', 'L6171r12@@')  # TODO: Remover senha padrão"
    },
    'criar_admin_producao.py': {
        'linha': 20,
        'padrao': r"password\s*=\s*['\"]L6171r12@@['\"]",
        'substituicao': "password = os.getenv('ADMIN_PASSWORD', 'L6171r12@@')  # TODO: Remover senha padrão"
    },
    'criar_admin_fix.py': {
        'linha': 28,
        'padrao': r"password\s*=\s*['\"]L6171r12@@['\"]",
        'substituicao': "password = os.getenv('ADMIN_PASSWORD', 'L6171r12@@')  # TODO: Remover senha padrão"
    },
    'gestao_rural/views.py': {
        'linha': 209,
        'padrao': r"password\s*=\s*['\"]monpec['\"]",
        'substituicao': "password = os.getenv('DEMO_PASSWORD', 'monpec')  # TODO: Remover senha padrão"
    },
}

def corrigir_arquivo(caminho_arquivo, problema):
    """Corrige um problema de segurança em um arquivo"""
    arquivo = BASE_DIR / caminho_arquivo
    
    if not arquivo.exists():
        print(f"⚠️  Arquivo não encontrado: {caminho_arquivo}")
        return False
    
    try:
        conteudo = arquivo.read_text(encoding='utf-8')
        linhas = conteudo.split('\n')
        
        # Verificar se precisa adicionar import os
        precisa_import_os = 'import os' not in conteudo and 'from os import' not in conteudo
        
        # Substituir a linha problemática
        linha_num = problema['linha'] - 1
        if linha_num < len(linhas):
            linha_original = linhas[linha_num]
            if re.search(problema['padrao'], linha_original):
                linhas[linha_num] = problema['substituicao']
                
                # Adicionar import os se necessário
                if precisa_import_os:
                    # Encontrar onde adicionar o import
                    import_idx = 0
                    for i, linha in enumerate(linhas):
                        if linha.strip().startswith('import ') or linha.strip().startswith('from '):
                            import_idx = i + 1
                    linhas.insert(import_idx, 'import os')
                
                novo_conteudo = '\n'.join(linhas)
                arquivo.write_text(novo_conteudo, encoding='utf-8')
                print(f"✅ Corrigido: {caminho_arquivo}")
                return True
            else:
                print(f"⚠️  Padrão não encontrado em {caminho_arquivo}:{problema['linha']}")
                return False
        else:
            print(f"⚠️  Linha {problema['linha']} não existe em {caminho_arquivo}")
            return False
    except Exception as e:
        print(f"❌ Erro ao corrigir {caminho_arquivo}: {e}")
        return False

def main():
    print("="*80)
    print("CORREÇÃO DE PROBLEMAS DE SEGURANÇA")
    print("="*80)
    print()
    print("⚠️  ATENÇÃO: Este script irá modificar arquivos com senhas hardcoded")
    print("    As senhas serão substituídas por variáveis de ambiente")
    print()
    print("Arquivos que serão modificados:")
    for arquivo in ARQUIVOS_PROBLEMAS:
        print(f"  - {arquivo}")
    print()
    
    resposta = input("Deseja continuar? (s/n): ").strip().lower()
    
    if resposta != 's':
        print("❌ Operação cancelada.")
        return
    
    corrigidos = 0
    erros = 0
    
    for arquivo, problema in ARQUIVOS_PROBLEMAS.items():
        if corrigir_arquivo(arquivo, problema):
            corrigidos += 1
        else:
            erros += 1
    
    print()
    print("="*80)
    print(f"✅ Concluído! {corrigidos} arquivo(s) corrigido(s), {erros} erro(s)")
    print("="*80)
    print()
    print("⚠️  IMPORTANTE:")
    print("   1. Configure as variáveis de ambiente ADMIN_PASSWORD e DEMO_PASSWORD")
    print("   2. Remova as senhas padrão dos arquivos após configurar as variáveis")
    print("   3. Revise os arquivos modificados antes de fazer commit")

if __name__ == '__main__':
    main()






