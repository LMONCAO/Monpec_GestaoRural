#!/usr/bin/env python
"""
Teste direto do endpoint de checkout
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

print('Testando endpoint de checkout...')

client = Client()
User = get_user_model()

# Buscar usuário
user = User.objects.filter(is_active=True).first()
if not user:
    print('ERRO: Nenhum usuário encontrado')
    exit(1)

print(f'Usuário encontrado: {user.username}')
client.force_login(user)

# Fazer requisição
print('Enviando requisição POST...')
response = client.post('/assinaturas/plano/basico/checkout/', {
    'nome': 'João Silva',
    'email': 'teste@teste.com',
    'gateway': 'mercadopago'
}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

print(f'Status: {response.status_code}')
print(f'Content-Type: {response.get("Content-Type", "N/A")}')
print('Conteúdo da resposta:')
print(response.content.decode('utf-8', errors='replace')[:1000])

if response.status_code == 200:
    print('✅ Requisição bem-sucedida!')
else:
    print('❌ Erro na requisição!')
