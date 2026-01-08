#!/usr/bin/env python
"""
Script para testar o endpoint de checkout diretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from gestao_rural.models import PlanoAssinatura
from gestao_rural.views_assinaturas import iniciar_checkout

def test_checkout():
    print("=== TESTANDO CHECKOUT DIRETAMENTE ===")

    # Obter dados necessários
    user = User.objects.filter(is_superuser=True).first()
    plano = PlanoAssinatura.objects.filter(slug='basico').first()

    print(f"Usuário encontrado: {user.username if user else 'Nenhum'}")
    print(f"Plano encontrado: {plano.slug if plano else 'Nenhum'}")

    if not user or not plano:
        print("❌ Usuário ou plano não encontrado")
        return

    # Criar request factory
    factory = RequestFactory()

    # Simular POST request
    data = {
        'user_id': str(user.id),
        'nome': 'João Silva',
        'email': 'joao@teste.com'
    }

    request = factory.post(f'/assinaturas/plano/{plano.slug}/checkout/', data)
    request.user = user

    print(f"Fazendo requisição POST para plano {plano.slug}")

    try:
        response = iniciar_checkout(request, plano.slug)
        print(f"Status da resposta: {response.status_code}")
        print(f"Conteúdo: {response.content}")

        import json
        data = json.loads(response.content)
        print("Dados JSON:", data)

    except Exception as e:
        print(f"❌ Erro ao chamar função: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_checkout()
