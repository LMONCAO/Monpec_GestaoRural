#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para garantir que o usuário admin existe em produção
Execute: python garantir_admin_producao.py
"""
import os
import sys
import django

# Configurar Django para produção
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

def main():
    """Garante que o admin existe com a senha correta"""
    print("=" * 60)
    print("GARANTINDO USUÁRIO ADMIN EM PRODUÇÃO")
    print("=" * 60)
    print()
    
    # Usar senha padrão ou variável de ambiente
    senha = os.getenv('ADMIN_PASSWORD', 'L6171r12@@')
    username = 'admin'
    email = 'admin@monpec.com.br'
    
    print(f"Configuração:")
    print(f"  - Username: {username}")
    print(f"  - Email: {email}")
    print(f"  - Senha: {'*' * len(senha)}")
    print()
    
    try:
        # Usar o comando management
        print("Executando comando garantir_admin...")
        call_command('garantir_admin', 
                    username=username,
                    email=email,
                    senha=senha,
                    forcar=False)
        
        # Verificar se funcionou
        user = User.objects.filter(username=username).first()
        if user:
            print()
            print("Verificando autenticação...")
            user_auth = authenticate(username=username, password=senha)
            if user_auth:
                print("✅ SUCESSO! Admin está pronto para uso.")
                print()
                print(f"Credenciais:")
                print(f"  Username: {username}")
                print(f"  Senha: {senha}")
                return True
            else:
                print("⚠️ AVISO: Usuário existe mas autenticação falhou.")
                print("   Tente executar novamente com --forcar")
                return False
        else:
            print("❌ ERRO: Usuário não foi criado.")
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = main()
    sys.exit(0 if sucesso else 1)


