#!/usr/bin/env python
"""
Script para configurar o sistema rural
Executa migrações e popula as categorias de animais
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.core.management.commands.migrate import Command as MigrateCommand
from gestao_rural.management.commands.popular_categorias import Command as PopularCategoriasCommand

def main():
    print("🚀 Configurando Sistema Rural...")
    
    # 1. Executar migrações
    print("\n📦 Executando migrações do banco de dados...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrações executadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao executar migrações: {e}")
        return False
    
    # 2. Popular categorias
    print("\n🐄 Populando categorias de animais...")
    try:
        popular_categorias = PopularCategoriasCommand()
        popular_categorias.handle()
        print("✅ Categorias populadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao popular categorias: {e}")
        return False
    
    # 3. Criar superusuário
    print("\n👤 Criando superusuário...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("✅ Superusuário criado: admin/admin123")
        else:
            print("ℹ️ Superusuário já existe")
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
    
    print("\n🎉 Sistema configurado com sucesso!")
    print("\nPara executar o servidor:")
    print("python manage.py runserver")
    print("\nPara acessar o admin:")
    print("http://127.0.0.1:8000/admin/")
    print("Usuário: admin | Senha: admin123")
    
    return True

if __name__ == '__main__':
    main()

