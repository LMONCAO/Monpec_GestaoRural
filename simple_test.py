#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

client = Client()
User = get_user_model()

user = User.objects.filter(is_active=True).first()
if user:
    client.force_login(user)
    print(f'User: {user.username}')

    response = client.post('/assinaturas/plano/basico/checkout/', {
        'nome': 'João Silva',
        'email': 'teste@teste.com',
        'gateway': 'mercadopago'
    })

    print(f'Status: {response.status_code}')
    content = response.content.decode('utf-8', errors='replace')
    print(f'Content length: {len(content)}')
    print('First 200 chars:')
    print(content[:200])
else:
    print('No user found')
