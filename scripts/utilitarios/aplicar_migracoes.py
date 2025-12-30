"""Script para aplicar migrações do Mercado Pago - encontra o diretório automaticamente."""

import os
import sys
import django
from pathlib import Path

# Encontrar o diretório do projeto
script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Verificando se manage.py existe: {os.path.exists('manage.py')}")
    sys.exit(1)

from django.core.management import call_command

if __name__ == '__main__':
    print("=" * 60)
    print("Aplicando migracoes do Mercado Pago...")
    print("=" * 60)
    print(f"Diretorio: {os.getcwd()}")
    print()
    
    print("1. Criando migracoes...")
    try:
        call_command('makemigrations', 'gestao_rural', verbosity=2)
        print("OK - Migracoes criadas com sucesso!")
    except Exception as e:
        print(f"ERRO ao criar migracoes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("2. Aplicando migracoes...")
    try:
        call_command('migrate', 'gestao_rural', verbosity=2)
        print("OK - Migracoes aplicadas com sucesso!")
    except Exception as e:
        print(f"ERRO ao aplicar migracoes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("CONCLUIDO! Os novos campos do Mercado Pago foram adicionados.")
    print("=" * 60)
    print()
    print("Agora você pode:")
    print("  - Acessar /assinaturas/ sem erros")
    print("  - Usar o Mercado Pago como gateway")
    print("  - Criar assinaturas normalmente")
    print()

