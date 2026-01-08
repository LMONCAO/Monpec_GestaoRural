#!/usr/bin/env python
"""
Script para testar o fluxo completo de demonstração
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

def testar_fluxo_demo():
    print("="*70)
    print("TESTANDO FLUXO COMPLETO DE DEMONSTRACAO")
    print("="*70)

    client = Client()

    # 1. Testar criação de usuário demo
    print("\n1. Criando usuário demo...")
    from django.urls import reverse
    url = reverse('criar_usuario_demonstracao')
    data = 'nome_completo=Usuario%20Teste%20Demo&email=teste_demo_123%40example.com&telefone=%2867%29%2099999-9999'
    response = client.post(url, data, content_type='application/x-www-form-urlencoded')

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            print(f"Redirect URL: {data.get('redirect_url')}")

            if data.get('success') and data.get('redirect_url'):
                # 2. Testar acesso à demo_loading
                print("\n2. Testando acesso a demo_loading...")
                response2 = client.get(data['redirect_url'])
                print(f"Demo loading status: {response2.status_code}")
                if response2.status_code == 200:
                    print("✅ Demo loading acessível")
                else:
                    print(f"❌ Problema no demo_loading: {response2.status_code}")

                # 3. Simular redirecionamento para demo_setup
                print("\n3. Testando acesso a demo_setup...")
                response3 = client.get('/demo/setup/')
                print(f"Demo setup status: {response3.status_code}")
                if response3.status_code == 302:  # Redirecionamento
                    redirect_to = response3.get('Location', 'N/A')
                    print(f"✅ Redirecionamento para: {redirect_to}")
                else:
                    print(f"❌ Demo setup não redirecionou: {response3.status_code}")

        except Exception as e:
            print(f"Erro ao processar resposta: {e}")
    else:
        print(f"Erro na criação do usuário: {response.status_code}")
        print(f"Conteúdo: {response.content.decode()}")

    print("\n" + "="*70)

if __name__ == '__main__':
    testar_fluxo_demo()
