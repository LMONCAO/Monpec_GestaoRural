#!/usr/bin/env python
"""
Script para testar o usuário admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.test import Client

def testar_admin():
    print("Testando usuário admin...")

    User = get_user_model()

    # Verificar se admin existe
    admin = User.objects.filter(username='admin').first()
    if not admin:
        print("Usuario admin nao existe")
        return

    print("Usuario admin existe")
    print(f"   - Email: {admin.email}")
    print(f"   - Superuser: {admin.is_superuser}")
    print(f"   - Active: {admin.is_active}")

    # Testar senha
    senha_correta = admin.check_password('L6171r12@@')
    print(f"   - Senha correta: {senha_correta}")

    # Testar autenticação
    user_auth = authenticate(username='admin', password='L6171r12@@')
    print(f"   - Autenticação funciona: {user_auth is not None}")

    # Testar login via client
    client = Client()
    response = client.post('/login/', {
        'username': 'admin',
        'password': 'L6171r12@@'
    })

    print(f"   - Login via POST status: {response.status_code}")
    print(f"   - Redirect: {response.get('Location', 'Nenhum')}")

    if response.status_code == 302:
        # Seguir redirect
        redirect_url = response.get('Location')
        if redirect_url:
            response2 = client.get(redirect_url)
            print(f"   - Página após login: {response2.status_code}")

if __name__ == '__main__':
    testar_admin()