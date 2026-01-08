#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client

def testar_criacao():
    client = Client()

    print("Testando criação de usuário demo...")
    response = client.post('/criar-usuario-demonstracao/', {
        'nome_completo': 'Teste Simples',
        'email': 'teste_simples_999@example.com',
        'telefone': '(67) 99999-9999'
    })

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Usuario criado com sucesso!")
        print(f"Redirect URL: {data.get('redirect_url')}")

        # Testar o redirect
        if data.get('redirect_url'):
            print(f"\nTestando acesso a {data['redirect_url']}...")
            response2 = client.get(data['redirect_url'])
            print(f"Status do loading: {response2.status_code}")

            if response2.status_code == 302:
                redirect_url = response2.get('Location', 'N/A')
                print(f"Redirecionando para: {redirect_url}")

                # Testar o destino final
                if redirect_url.startswith('/'):
                    print(f"\nTestando destino final {redirect_url}...")
                    response3 = client.get(redirect_url)
                    print(f"Status final: {response3.status_code}")
            else:
                print("Demo loading acessivel")
    else:
        print("Erro na criacao")
        print(response.content.decode('utf-8', errors='ignore'))

if __name__ == '__main__':
    testar_criacao()
