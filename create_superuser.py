#!/usr/bin/env python
"""
Script para criar superusuário se não existir
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User

# Verificar se já existe um superusuário
if not User.objects.filter(is_superuser=True).exists():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@monpec.com.br')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print('✅ Superusuário "{}" criado com sucesso!'.format(username))
else:
    print('✅ Superusuário já existe')


