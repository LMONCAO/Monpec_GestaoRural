#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from gestao_rural.models import Propriedade

def testar_fluxo_completo():
    print("="*70)
    print("TESTANDO FLUXO COMPLETO DE DEMONSTRAÇÃO")
    print("="*70)

    client = Client()

    # 1. Testar criação de usuário demo
    print("\n1. Criando usuário demo...")
    import time
    timestamp = str(int(time.time()))
    response = client.post('/criar-usuario-demonstracao/', {
        'nome_completo': f'Usuario Demo {timestamp}',
        'email': f'demo_{timestamp}@testemonpec.com.br',
        'telefone': '(67) 99999-9999'
    })

    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Conteúdo do erro: {response.content.decode('utf-8', errors='ignore')}")
        return

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message')}")
            print(f"Redirect URL: {data.get('redirect_url')}")

            if data.get('redirect_url'):
                # 2. Testar acesso à demo_loading
                print(f"\n2. Testando acesso a {data['redirect_url']}...")
                response2 = client.get(data['redirect_url'])
                print(f"Status: {response2.status_code}")

                if response2.status_code == 302:
                    redirect_to = response2.get('Location', 'N/A')
                    print(f"Redirecionamento para: {redirect_to}")

                    # 3. Testar o redirecionamento final
                    if redirect_to and redirect_to.startswith('/'):
                        print(f"\n3. Testando redirecionamento para {redirect_to}...")
                        response3 = client.get(redirect_to)
                        print(f"Status final: {response3.status_code}")

                        if response3.status_code == 200:
                            print("✅ Redirecionamento funcionando!")
                        else:
                            print("❌ Erro no redirecionamento final")
                    else:
                        print("❌ URL de redirecionamento inválida")
                elif response2.status_code == 200:
                    print("✅ Demo loading acessível diretamente")
                else:
                    print(f"❌ Erro na demo_loading: {response2.status_code}")
        except Exception as e:
            print(f"Erro ao processar resposta: {e}")
    else:
        print(f"Erro na criação do usuário: {response.status_code}")

    print("\n" + "="*70)

if __name__ == '__main__':
    testar_fluxo_completo()
