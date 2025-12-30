"""Script para aplicar migrações do Mercado Pago."""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    print("🔄 Criando migrações...")
    try:
        call_command('makemigrations', 'gestao_rural', verbosity=2)
        print("✅ Migrações criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar migrações: {e}")
        sys.exit(1)
    
    print("\n🔄 Aplicando migrações...")
    try:
        call_command('migrate', 'gestao_rural', verbosity=2)
        print("✅ Migrações aplicadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao aplicar migrações: {e}")
        sys.exit(1)
    
    print("\n✅ Concluído! Os novos campos do Mercado Pago foram adicionados ao banco de dados.")





























