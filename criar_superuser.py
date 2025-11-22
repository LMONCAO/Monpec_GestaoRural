#!/usr/bin/env python
"""Script para criar superusuário do Django"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Criar superusuário se não existir
username = 'admin'
email = 'admin@monpec.com.br'
password = 'Monpec2025!'

if User.objects.filter(username=username).exists():
    print(f'Superusuário "{username}" já existe!')
else:
    User.objects.create_superuser(username, email, password)
    print(f'Superusuário "{username}" criado com sucesso!')
    print(f'Email: {email}')
    print(f'Senha: {password}')


