#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir a senha do usuário admin
Execute: python CORRIGIR_SENHA_ADMIN.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

def corrigir_senha_admin():
    """Corrige a senha do usuário admin"""
    username = 'admin'
    # ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
    password = os.getenv('ADMIN_PASSWORD')
    if not password:
        print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
        print("   Configure a variável antes de executar:")
        print("   export ADMIN_PASSWORD='sua-senha-segura'")
        return False
    
    print("=" * 60)
    print("CORRIGINDO SENHA DO USUÁRIO ADMIN")
    print("=" * 60)
    print()
    
    try:
        # Buscar ou criar usuário
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': 'admin@monpec.com.br',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        
        if created:
            print(f"✅ Usuário '{username}' CRIADO")
        else:
            print(f"✅ Usuário '{username}' ENCONTRADO")
        
        print(f"   - Email: {user.email}")
        print(f"   - Ativo: {user.is_active}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Superuser: {user.is_superuser}")
        print()
        
        # Redefinir senha
        print(f"Redefinindo senha...")
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.email = 'admin@monpec.com.br'
        user.save()
        print(f"✅ Senha redefinida!")
        print()
        
        # Verificar se a senha está correta
        print("Verificando senha...")
        if user.check_password(password):
            print(f"✅ Senha verificada: CORRETA")
        else:
            print(f"❌ ERRO: Senha ainda está incorreta após redefinição")
            return False
        
        # Testar autenticação
        print()
        print("Testando autenticação Django...")
        user_auth = authenticate(username=username, password=password)
        if user_auth:
            print(f"✅ Autenticação Django: SUCESSO")
            print(f"   - ID: {user_auth.id}")
            print(f"   - Username: {user_auth.username}")
        else:
            print(f"❌ Autenticação Django: FALHOU")
            print("   Isso indica um problema mais profundo no sistema")
            return False
        
        print()
        print("=" * 60)
        print("✅ SUCESSO! Senha corrigida e testada")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print()
        print("Agora você pode fazer login no sistema!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = corrigir_senha_admin()
    sys.exit(0 if sucesso else 1)





