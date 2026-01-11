#!/usr/bin/env python
"""
Script para debugar o erro 500 no checkout do Mercado Pago
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def debug_checkout_error():
    print('=== DEBUG CHECKOUT 500 ===')

    # Configurar cliente de teste
    client = Client()
    user = User.objects.get(username='admin')
    client.force_login(user)

    # Headers que o JavaScript envia
    headers = {
        'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'
    }

    # Dados que o JavaScript envia
    post_data = {
        'gateway': 'mercadopago',
        'nome': 'Rafael',
        'email': 'rafael@monpec.com.br'
    }

    print('Fazendo requisição POST para /assinaturas/plano/basico/checkout/')
    print(f'Dados: {post_data}')
    print(f'Headers: {headers}')

    try:
        response = client.post(
            '/assinaturas/plano/basico/checkout/',
            data=post_data,
            content_type='application/x-www-form-urlencoded',
            **headers
        )

        print(f'\nStatus Code: {response.status_code}')
        print(f'Content-Type: {response.get("Content-Type")}')

        content = response.content.decode()

        if response.status_code == 500:
            print('\n=== ERRO 500 - PROCURANDO TRACEBACK ===')

            # Procurar por traceback na resposta
            if 'Traceback' in content:
                print('✅ Traceback encontrado!')
                lines = content.split('\n')
                traceback_start = None

                for i, line in enumerate(lines):
                    if 'Traceback (most recent call last):' in line:
                        traceback_start = i
                        break

                if traceback_start is not None:
                    print('\n--- TRACEBACK ---')
                    for i in range(traceback_start, min(traceback_start + 30, len(lines))):
                        if lines[i].strip():
                            print(f'{i-traceback_start+1:2d}: {lines[i]}')
                        if i > traceback_start + 20 and 'Internal Server Error' in lines[i]:
                            break
                    print('--- FIM TRACEBACK ---\n')
                else:
                    print('Traceback encontrado mas não conseguiu extrair')
            else:
                print('❌ Nenhum traceback encontrado na resposta')

            # Mostrar início da resposta HTML para debug
            print('Conteúdo da resposta (primeiras 300 chars):')
            print(repr(content[:300]))

        elif response.status_code == 200:
            print('✅ Status 200 - tentativa de parse JSON')
            try:
                import json
                data = json.loads(content)
                print(f'Resposta JSON: {data}')
            except:
                print('Não é JSON válido')
                print(f'Conteúdo: {content[:200]}')
        else:
            print(f'Status inesperado: {response.status_code}')
            print(f'Conteúdo: {content[:300]}')

    except Exception as e:
        print(f'\n❌ EXCEÇÃO DURANTE TESTE: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_checkout_error()




