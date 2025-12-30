#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para resolver problemas com dumpdata:
1. Aplica migrações pendentes
2. Cria migrações se necessário
3. Faz dump com encoding UTF-8 correto
"""
import os
import sys
import subprocess
import io

# Configurar encoding UTF-8 para stdout/stderr
if sys.platform == 'win32':
    # Windows: configurar console para UTF-8
    import codecs
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(cmd, description):
    """Executa um comando Django e retorna True se sucesso"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Executando: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0:
            print(f"\n✓ {description} - SUCESSO")
            return True
        else:
            print(f"\n✗ {description} - FALHOU (código: {result.returncode})")
            return False
    except Exception as e:
        print(f"\n✗ Erro ao executar comando: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("RESOLVER PROBLEMAS COM DUMPDATA")
    print("="*60)
    
    # Verificar se manage.py existe
    if not os.path.exists('manage.py'):
        print("\n✗ ERRO: manage.py não encontrado!")
        print("   Execute este script na raiz do projeto Django.")
        return 1
    
    # 1. Criar migrações se necessário
    print("\n[1/4] Verificando e criando migrações...")
    run_command(
        ['python', 'manage.py', 'makemigrations'],
        "Criar migrações"
    )
    
    # 2. Aplicar migrações
    print("\n[2/4] Aplicando migrações...")
    if not run_command(
        ['python', 'manage.py', 'migrate'],
        "Aplicar migrações"
    ):
        print("\n⚠ AVISO: Algumas migrações podem ter falhado.")
        print("   Verifique os erros acima antes de continuar.")
        resposta = input("\nDeseja continuar mesmo assim? (s/n): ")
        if resposta.lower() != 's':
            return 1
    
    # 3. Verificar status das migrações
    print("\n[3/4] Verificando status das migrações...")
    run_command(
        ['python', 'manage.py', 'showmigrations', 'gestao_rural'],
        "Status das migrações"
    )
    
    # 4. Fazer dump com encoding UTF-8
    print("\n[4/4] Fazendo dump dos dados (UTF-8)...")
    output_file = 'dados_backup.json'
    
    # Configurar variável de ambiente para UTF-8
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    cmd = [
        'python', 'manage.py', 'dumpdata',
        '--natural-foreign',
        '--natural-primary',
        '-o', output_file
    ]
    
    print(f"\n{'='*60}")
    print("Fazendo dump dos dados")
    print(f"{'='*60}")
    print(f"Executando: {' '.join(cmd)}")
    print(f"Arquivo de saída: {output_file}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"\n✓ Dump criado com sucesso!")
                print(f"  Arquivo: {output_file}")
                print(f"  Tamanho: {size:,} bytes ({size/1024/1024:.2f} MB)")
                return 0
            else:
                print(f"\n✗ Dump falhou: arquivo não foi criado")
                return 1
        else:
            print(f"\n✗ Dump falhou (código: {result.returncode})")
            return 1
    except Exception as e:
        print(f"\n✗ Erro ao fazer dump: {e}")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nErro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

