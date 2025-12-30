#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para fazer dump dos dados com encoding UTF-8 correto.
Usa subprocess para redirecionar saída para arquivo UTF-8.
"""
import os
import sys
import subprocess

def main():
    output_file = 'dados_backup.json'
    
    print(f"\n{'='*60}")
    print("FAZER DUMP DOS DADOS (UTF-8)")
    print(f"{'='*60}\n")
    print(f"Arquivo de saída: {output_file}")
    print(f"Encoding: UTF-8")
    print()
    
    # Configurar ambiente para UTF-8
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUTF8'] = '1'
    
    # Remover arquivo anterior se existir
    if os.path.exists(output_file):
        print(f"Removendo arquivo anterior: {output_file}")
        os.remove(output_file)
    
    print("Executando dumpdata...")
    print("(Isso pode levar alguns minutos dependendo do tamanho do banco)\n")
    
    try:
        # Executar dumpdata e redirecionar para arquivo UTF-8
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            result = subprocess.run(
                [sys.executable, 'manage.py', 'dumpdata',
                 '--natural-foreign', '--natural-primary'],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
        
        if result.returncode != 0:
            # Mostrar erros
            if result.stderr:
                print("Erros durante o dump:")
                print(result.stderr)
            
            # Verificar se arquivo foi criado mesmo com erros
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print("\n⚠ AVISO: Houve erros, mas o arquivo foi criado.")
                print("Verifique os erros acima.")
            else:
                print("\n✗ ERRO: Dump falhou completamente.")
                return 1
        
        # Verificar se arquivo foi criado
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            if size > 0:
                print(f"\n{'='*60}")
                print("✓ DUMP CRIADO COM SUCESSO!")
                print(f"{'='*60}")
                print(f"\nArquivo: {output_file}")
                print(f"Tamanho: {size:,} bytes ({size/1024/1024:.2f} MB)")
                return 0
            else:
                print(f"\n✗ ERRO: Arquivo foi criado mas está vazio!")
                return 1
        else:
            print(f"\n✗ ERRO: Arquivo não foi criado!")
            return 1
            
    except Exception as e:
        print(f"\n✗ ERRO ao fazer dump: {e}")
        import traceback
        traceback.print_exc()
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

