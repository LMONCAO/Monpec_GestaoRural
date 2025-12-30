#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para fazer dump dos dados com encoding UTF-8 correto.
Resolve problemas com caracteres especiais no Windows.
"""
import os
import sys
import io
import json

# Forçar encoding UTF-8
if sys.platform == 'win32':
    # Windows: configurar stdout/stderr para UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.core.management import call_command
from django.core import serializers
from django.db import connections

def main():
    output_file = 'dados_backup.json'
    
    print(f"\n{'='*60}")
    print("FAZER DUMP DOS DADOS (UTF-8)")
    print(f"{'='*60}\n")
    print(f"Arquivo de saída: {output_file}")
    print(f"Encoding: UTF-8")
    print()
    
    try:
        # Método alternativo: serializar diretamente com UTF-8
        print("Serializando dados...")
        
        # Obter todos os apps e modelos
        from django.apps import apps
        all_objects = []
        
        # Serializar todos os modelos de todos os apps
        for app_config in apps.get_app_configs():
            app_label = app_config.label
            if app_label in ['admin', 'auth', 'contenttypes', 'sessions', 'gestao_rural']:
                for model in app_config.get_models():
                    try:
                        queryset = model.objects.all()
                        if queryset.exists():
                            print(f"  Serializando {app_label}.{model.__name__}... ({queryset.count()} objetos)")
                            for obj in queryset:
                                all_objects.append(obj)
                    except Exception as e:
                        print(f"  ⚠ Erro ao serializar {app_label}.{model.__name__}: {e}")
                        continue
        
        print(f"\nTotal de objetos: {len(all_objects)}")
        print("Escrevendo arquivo JSON com UTF-8...")
        
        # Escrever JSON diretamente com UTF-8
        with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
            serializers.serialize(
                'json',
                all_objects,
                indent=2,
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True,
                stream=f,
                ensure_ascii=False  # Importante: permite caracteres Unicode
            )
        
        # Verificar se arquivo foi criado
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"\n{'='*60}")
            print("✓ DUMP CRIADO COM SUCESSO!")
            print(f"{'='*60}")
            print(f"\nArquivo: {output_file}")
            print(f"Tamanho: {size:,} bytes ({size/1024/1024:.2f} MB)")
            return 0
        else:
            print(f"\n✗ ERRO: Arquivo não foi criado!")
            return 1
            
    except Exception as e:
        print(f"\n✗ ERRO ao fazer dump: {e}")
        import traceback
        traceback.print_exc()
        
        # Tentar método alternativo mais simples
        print("\nTentando método alternativo...")
        try:
            # Usar call_command mas redirecionar para arquivo UTF-8
            import subprocess
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                result = subprocess.run(
                    [sys.executable, 'manage.py', 'dumpdata', 
                     '--natural-foreign', '--natural-primary'],
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    env=env
                )
            
            if result.returncode == 0 and os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"\n✓ DUMP CRIADO COM SUCESSO (método alternativo)!")
                print(f"Arquivo: {output_file}")
                print(f"Tamanho: {size:,} bytes ({size/1024/1024:.2f} MB)")
                return 0
        except Exception as e2:
            print(f"✗ Método alternativo também falhou: {e2}")
        
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

