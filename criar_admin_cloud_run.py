#!/usr/bin/env python
"""
Script para criar/atualizar superusuário no Cloud Run
Execute via: gcloud run jobs execute criar-admin --region us-central1
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Credenciais do admin
username = 'admin'
email = 'admin@monpec.com.br'
password = 'Monpec2025!'

print("=" * 60)
print("CRIANDO/ATUALIZANDO SUPERUSUÁRIO")
print("=" * 60)
print()

if User.objects.filter(username=username).exists():
    usuario = User.objects.get(username=username)
    usuario.set_password(password)
    usuario.is_superuser = True
    usuario.is_staff = True
    usuario.is_active = True
    usuario.email = email
    usuario.save()
    print(f'✅ Superusuário "{username}" atualizado com sucesso!')
else:
    User.objects.create_superuser(username, email, password)
    print(f'✅ Superusuário "{username}" criado com sucesso!')

print()
print('=' * 60)
print('CREDENCIAIS DE ACESSO:')
print('=' * 60)
print(f'Usuário: {username}')
print(f'Senha: {password}')
print('=' * 60)

