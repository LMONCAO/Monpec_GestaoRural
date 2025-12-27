#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para substituir senhas hardcoded por uso de variáveis de ambiente
nos scripts de administração do sistema.

Uso:
    python scripts/corrigir_senhas_hardcoded.py
"""
import os
import re
import sys
from pathlib import Path

# Padrão para encontrar senhas hardcoded comuns
PASSWORD_PATTERNS = [
    r"password\s*=\s*['\"]L6171r12@@['\"]",
    r"password\s*=\s*['\"][^'\"]+['\"]",  # Qualquer password = "algo"
    r"'L6171r12@@'",
    r'"L6171r12@@"',
]

# Substituição segura
REPLACEMENT = """password = os.getenv('ADMIN_PASSWORD')
    if not password:
        print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
        print("   Configure a variável antes de executar:")
        print("   export ADMIN_PASSWORD='sua-senha-segura'")
        sys.exit(1)"""


def corrigir_arquivo(caminho_arquivo):
    """Corrige senhas hardcoded em um arquivo"""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        conteudo_original = conteudo
        modificado = False
        
        # Verificar se já tem os.getenv('ADMIN_PASSWORD')
        if "os.getenv('ADMIN_PASSWORD')" in conteudo or 'os.getenv("ADMIN_PASSWORD")' in conteudo:
            print(f"⚠️  {caminho_arquivo}: Já usa variável de ambiente")
            return False
        
        # Substituir padrões comuns
        for pattern in PASSWORD_PATTERNS:
            matches = re.finditer(pattern, conteudo, re.IGNORECASE)
            for match in matches:
                linha = conteudo[:match.start()].count('\n') + 1
                
                # Tentar substituir de forma inteligente
                # Procurar por "password = 'senha'" em uma linha
                linha_match = re.search(rf'^\s*password\s*=\s*[^#\n]*{re.escape(match.group())}', 
                                       conteudo, re.MULTILINE)
                
                if linha_match:
                    # Substituir toda a atribuição
                    if 'import os' not in conteudo:
                        # Adicionar import os se não existir
                        imports_match = re.search(r'^(import\s+sys)', conteudo, re.MULTILINE)
                        if imports_match:
                            conteudo = conteudo[:imports_match.end()] + '\nimport os' + conteudo[imports_match.end():]
                        elif 'import os' not in conteudo:
                            # Adicionar no início após encoding
                            encoding_match = re.search(r'#.*coding.*\n', conteudo)
                            if encoding_match:
                                pos = encoding_match.end()
                            else:
                                pos = 0
                            conteudo = conteudo[:pos] + 'import os\nimport sys\n' + conteudo[pos:]
                    
                    # Substituir a linha
                    antiga_linha = linha_match.group(0)
                    # Criar substituição com indentação correta
                    indentacao = len(antiga_linha) - len(antiga_linha.lstrip())
                    nova_linha = ' ' * indentacao + REPLACEMENT.replace('\n    ', '\n' + ' ' * indentacao)
                    
                    conteudo = conteudo.replace(antiga_linha, nova_linha, 1)
                    modificado = True
                    print(f"✅ {caminho_arquivo}: Linha {linha} corrigida")
                    break
        
        if modificado:
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Erro ao processar {caminho_arquivo}: {e}")
        return False


def main():
    """Função principal"""
    base_dir = Path(__file__).parent.parent
    
    # Arquivos a verificar (scripts de admin)
    arquivos_alvo = [
        'corrigir_admin_agora.py',
        'CORRIGIR_SENHA_ADMIN.py',
        'criar_admin_simples.py',
        'fix_admin.py',
        'criar_admin_definitivo.py',
        'criar_admin_cloud_shell.py',
        'criar_admin_cloud_run.py',
        'criar_admin_cloud.py',
        'criar_admin_via_shell.py',
        'criar_admin.py',
        'redefinir_senha_admin.py',
        'verificar_admin.py',
    ]
    
    # Também procurar por padrões em todos os .py da raiz
    arquivos_encontrados = []
    for arquivo in base_dir.glob('*.py'):
        if arquivo.name not in ['manage.py', 'corrigir_senhas_hardcoded.py']:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                    # Verificar se tem senha hardcoded
                    if any(re.search(pattern, conteudo, re.IGNORECASE) for pattern in PASSWORD_PATTERNS):
                        if "os.getenv('ADMIN_PASSWORD')" not in conteudo:
                            arquivos_encontrados.append(arquivo)
            except:
                pass
    
    print("=" * 70)
    print("CORREÇÃO DE SENHAS HARDCODED")
    print("=" * 70)
    print()
    
    todos_arquivos = [base_dir / f for f in arquivos_alvo if (base_dir / f).exists()] + arquivos_encontrados
    
    if not todos_arquivos:
        print("✅ Nenhum arquivo com senha hardcoded encontrado!")
        return
    
    print(f"📁 Encontrados {len(todos_arquivos)} arquivo(s) para verificar:")
    for arquivo in todos_arquivos:
        print(f"   - {arquivo.name}")
    print()
    
    resposta = input("Deseja corrigir automaticamente? (s/N): ").strip().lower()
    if resposta != 's':
        print("❌ Operação cancelada.")
        return
    
    corrigidos = 0
    for arquivo in todos_arquivos:
        if corrigir_arquivo(arquivo):
            corrigidos += 1
    
    print()
    print("=" * 70)
    print(f"✅ Correção concluída: {corrigidos} arquivo(s) modificado(s)")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANTE:")
    print("   1. Revise as alterações antes de commitar")
    print("   2. Configure a variável ADMIN_PASSWORD nos ambientes")
    print("   3. Teste os scripts corrigidos")


if __name__ == '__main__':
    main()






























