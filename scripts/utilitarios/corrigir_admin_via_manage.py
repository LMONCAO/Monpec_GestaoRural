#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir admin via manage.py shell
Execute no servidor de produção:

python manage.py shell < corrigir_admin_via_manage.py

OU execute diretamente no shell do Django:

python manage.py shell
>>> exec(open('corrigir_admin_via_manage.py').read())
"""
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

username = 'admin'
# ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
import os
password = os.getenv('ADMIN_PASSWORD')
if not password:
    print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
    print("   Configure a variável antes de executar:")
    print("   export ADMIN_PASSWORD='sua-senha-segura'")
    exit(1)

print("=" * 70)
print("CORREÇÃO DO USUÁRIO ADMIN - PRODUÇÃO")
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
        exit(1)
    
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
        exit(1)
    
    print()
    print("=" * 70)
    print("✅ SUCESSO! Usuário admin corrigido e testado")
    print("=" * 70)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: admin@monpec.com.br")
    print()
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

