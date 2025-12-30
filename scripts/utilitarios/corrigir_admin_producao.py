#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir o usuário admin em PRODUÇÃO (monpec.com.br)
Execute este script no servidor de produção para garantir que o admin funcione.

Uso:
    python corrigir_admin_producao.py
"""
import os
import sys
import django

# Configurar Django para PRODUÇÃO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_producao')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

def corrigir_admin_producao():
    """Corrige o usuário admin em produção"""
    username = 'admin'
    # ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
    password = os.getenv('ADMIN_PASSWORD')
    if not password:
        print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
        print("   Configure a variável de ambiente antes de executar:")
        print("   export ADMIN_PASSWORD='sua-senha-segura'")
        print("   Ou no Windows:")
        print("   set ADMIN_PASSWORD=sua-senha-segura")
        return False
    
    print("=" * 70)
    print("CORREÇÃO DO USUÁRIO ADMIN - PRODUÇÃO (monpec.com.br)")
    print("=" * 70)
    print()
    
    try:
        # Verificar se o usuário existe
        try:
            user = User.objects.get(username=username)
            print(f"✅ Usuário '{username}' encontrado")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - is_active: {user.is_active}")
            print(f"   - is_staff: {user.is_staff}")
            print(f"   - is_superuser: {user.is_superuser}")
            print()
        except User.DoesNotExist:
            print(f"⚠️  Usuário '{username}' NÃO existe. Criando...")
            user = User.objects.create_user(
                username=username,
                email='admin@monpec.com.br',
                password=password
            )
            print(f"✅ Usuário '{username}' criado")
            print()
        
        # Garantir que o usuário está ativo e tem permissões
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.email = 'admin@monpec.com.br'
        
        # Redefinir senha (sempre, para garantir que está correta)
        print("Redefinindo senha...")
        user.set_password(password)
        user.save()
        print(f"✅ Senha redefinida para: {password}")
        print()
        
        # Verificar se a senha está correta
        print("Verificando senha...")
        if user.check_password(password):
            print(f"✅ Senha verificada: CORRETA")
        else:
            print(f"❌ ERRO: Senha ainda está incorreta após redefinição")
            return False
        
        # Testar autenticação completa
        print()
        print("Testando autenticação Django...")
        user_auth = authenticate(username=username, password=password)
        if user_auth:
            print(f"✅ Autenticação Django: SUCESSO")
            print(f"   - ID: {user_auth.id}")
            print(f"   - Username: {user_auth.username}")
            print(f"   - Email: {user_auth.email}")
        else:
            print(f"❌ Autenticação Django: FALHOU")
            print("   Isso pode indicar um problema no backend de autenticação")
            return False
        
        print()
        print("=" * 70)
        print("✅ SUCESSO! Usuário admin corrigido e testado")
        print("=" * 70)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Email: admin@monpec.com.br")
        print()
        print("Agora você pode fazer login em https://monpec.com.br/login/")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = corrigir_admin_producao()
    sys.exit(0 if sucesso else 1)

