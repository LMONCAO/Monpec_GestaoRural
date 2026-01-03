#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar/corrigir o usuário admin
Execute: python criar_admin_fix.py
"""
import os
import sys
import django

# Configurar Django
# Tentar usar settings_producao se estiver em produção, senão usar settings
if os.path.exists('sistema_rural/settings_producao.py'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_producao')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def criar_admin():
    """Cria ou atualiza o usuário admin"""
    username = os.getenv('ADMIN_USERNAME', 'admin')
    password = os.getenv('ADMIN_PASSWORD')
    email = os.getenv('ADMIN_EMAIL', 'admin@monpec.com.br')
    
    if not password:
        raise ValueError("ADMIN_PASSWORD não configurada! Configure a variável de ambiente ADMIN_PASSWORD.")
    
    print("=" * 60)
    print("CRIANDO/CORRIGINDO USUÁRIO ADMIN")
    print("=" * 60)
    print()
    
    try:
        # Buscar ou criar usuário
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        
        if created:
            print(f"✅ Usuário '{username}' CRIADO")
        else:
            print(f"✅ Usuário '{username}' ENCONTRADO")
            # Atualizar propriedades
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            print(f"   Propriedades atualizadas")
        
        print(f"   - Email: {user.email}")
        print(f"   - Ativo: {user.is_active}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Superuser: {user.is_superuser}")
        print()
        
        # Redefinir senha
        print(f"Redefinindo senha...")
        user.set_password(password)
        user.save()
        print(f"✅ Senha redefinida com sucesso!")
        print()
        print(f"Credenciais:")
        print(f"   Usuário: {username}")
        print(f"   Senha: {password}")
        print(f"   Email: {email}")
        print()
        print("=" * 60)
        print("✅ CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    criar_admin()

