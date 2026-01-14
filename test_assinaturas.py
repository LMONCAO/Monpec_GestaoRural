#!/usr/bin/env python
"""
Script para testar a view de assinaturas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def test_assinaturas():
    # Criar cliente de teste
    client = Client()

    print("=== TESTE DA VIEW DE ASSINATURAS ===")

    # Testar acesso sem login
    print("\n1. Testando acesso sem login...")
    response = client.get('/assinaturas/')
    print(f"Status: {response.status_code}")
    print(f"Redirect: {response.get('Location', 'Nenhum')}")

    # Testar login
    print("\n2. Fazendo login...")
    User = get_user_model()
    user = User.objects.filter(username='admin').first()
    if user:
        print(f"Usuario encontrado: {user.username}")
        client.force_login(user)

        print("\n3. Testando acesso com login...")
        response = client.get('/assinaturas/')
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print("Sucesso! Pagina carregou corretamente")
        elif response.status_code == 302:
            print(f"Redirect: {response.get('Location')}")
        else:
            print(f"Erro: Status {response.status_code}")
            print("Conteudo:", response.content.decode()[:200])
    else:
        print("Usuario admin nao encontrado")

if __name__ == '__main__':
    test_assinaturas()