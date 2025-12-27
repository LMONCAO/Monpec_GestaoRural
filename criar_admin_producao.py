#!/usr/bin/env python
"""
Script para criar/atualizar superusuário admin em produção
Execute via Cloud Run Job ou localmente
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Credenciais do admin
username = 'admin'
email = 'admin@monpec.com.br'
password = 'L6171r12@@'  # Senha fornecida pelo usuário

print("=" * 60)
print("CRIANDO/ATUALIZANDO SUPERUSUÁRIO ADMIN")
print("=" * 60)
print()

try:
    if User.objects.filter(username=username).exists():
        usuario = User.objects.get(username=username)
        usuario.set_password(password)
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.is_active = True
        usuario.email = email
        usuario.save()
        print(f'✅ Superusuário "{username}" ATUALIZADO com sucesso!')
        print(f'   Senha alterada para: {password}')
    else:
        User.objects.create_superuser(username, email, password)
        print(f'✅ Superusuário "{username}" CRIADO com sucesso!')
    
    print()
    print('=' * 60)
    print('CREDENCIAIS DE ACESSO:')
    print('=' * 60)
    print(f'Usuário: {username}')
    print(f'Email: {email}')
    print(f'Senha: {password}')
    print('=' * 60)
    print()
    print('✅ Pronto! Você já pode fazer login em https://monpec.com.br/login/')
    print()
    
except Exception as e:
    print(f'❌ ERRO ao criar/atualizar superusuário: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

