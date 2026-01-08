#!/usr/bin/env python
"""
Script para debug do checkout
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from gestao_rural.views_assinaturas import iniciar_checkout
from gestao_rural.models import PlanoAssinatura
import json

print('=== DEBUG CHECKOUT ===')

# Buscar usuário
User = get_user_model()
user = User.objects.filter(is_active=True).first()
if not user:
    print('ERRO: Nenhum usuario ativo encontrado')
    exit(1)

print(f'OK: Usuario encontrado: {user.username}')

# Buscar plano
plano = PlanoAssinatura.objects.filter(slug='basico', ativo=True).first()
if not plano:
    print('ERRO: Plano "basico" nao encontrado')
    exit(1)

print(f'OK: Plano encontrado: {plano.nome}')

# Criar request factory
factory = RequestFactory()

# Criar request POST
data = {
    'nome': 'João Silva',
    'email': 'teste@teste.com',
    'gateway': 'mercadopago'
}

request = factory.post(f'/assinaturas/plano/{plano.slug}/checkout/', data=data)
request.user = user

print('Enviando requisicao para iniciar_checkout...')

try:
    response = iniciar_checkout(request, plano.slug)
    print(f'Status: {response.status_code}')
    print(f'Conteudo: {response.content.decode()}')

    if response.status_code == 200:
        try:
            data = json.loads(response.content.decode())
            print('JSON valido:')
            print(f'  - checkout_url: {data.get("checkout_url", "NAO ENCONTRADO")}')
            print(f'  - session_id: {data.get("session_id", "NAO ENCONTRADO")}')
        except:
            print('Resposta nao e JSON valido')
    else:
        print('Status de erro')

except Exception as e:
    print(f'Excecao: {e}')
    import traceback
    traceback.print_exc()

print('=== FIM DEBUG ===')
