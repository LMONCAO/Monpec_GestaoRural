#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

# Criar cliente
client = Client()

# Fazer login
User = get_user_model()
user = User.objects.first()
if user:
    client.force_login(user)
    print(f'Login realizado como: {user.username}')

    # Testar endpoint
    response = client.post('/assinaturas/plano/basico/checkout/', {
        'nome': 'Teste Usuario',
        'email': 'teste@teste.com'
    })
    print(f'Status: {response.status_code}')
    print(f'Conteúdo: {response.content.decode()[:500]}')
else:
    print('Nenhum usuário encontrado')
