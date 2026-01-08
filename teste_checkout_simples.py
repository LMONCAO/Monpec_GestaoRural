#!/usr/bin/env python
"""
Teste simples do checkout para identificar o erro 500
"""
import os
import requests
import time

def testar_checkout():
    print('=== TESTE SIMPLES DO CHECKOUT ===')

    # Aguardar servidor iniciar
    time.sleep(3)

    # Criar sessão
    session = requests.Session()

    try:
        # 1. Fazer login
        print('1. Fazendo login...')
        login_response = session.post(
            'https://localhost:8000/login/',
            data={'username': 'admin', 'password': 'L6171r12@@'},
            verify=False,
            timeout=10
        )
        print(f'   Status login: {login_response.status_code}')

        if login_response.status_code != 302:
            print('   ❌ Login falhou')
            return

        # 2. Acessar página de assinaturas
        print('2. Acessando página de assinaturas...')
        assinaturas_response = session.get(
            'https://localhost:8000/assinaturas/',
            verify=False,
            timeout=10
        )
        print(f'   Status assinaturas: {assinaturas_response.status_code}')

        # 3. Extrair CSRF token
        print('3. Extraindo CSRF token...')
        csrf_token = None
        content = assinaturas_response.text
        import re
        match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', content)
        if match:
            csrf_token = match.group(1)
            print(f'   CSRF token encontrado: {csrf_token[:20]}...')
        else:
            print('   ❌ CSRF token não encontrado')
            return

        # 4. Fazer checkout
        print('4. Fazendo checkout...')
        headers = {
            'X-CSRFToken': csrf_token,
            'Referer': 'https://localhost:8000/assinaturas/',
            'X-Requested-With': 'XMLHttpRequest'
        }

        checkout_response = session.post(
            'https://localhost:8000/assinaturas/plano/basico/checkout/',
            data={
                'gateway': 'mercadopago',
                'nome': 'rafael',
                'email': 'rafael@monpec.com.br'
            },
            headers=headers,
            verify=False,
            timeout=15
        )

        print(f'   Status checkout: {checkout_response.status_code}')
        print(f'   Content-Type: {checkout_response.headers.get("content-type")}')

        if checkout_response.status_code == 200:
            print('   ✅ Checkout retornou 200!')
            try:
                data = checkout_response.json()
                print(f'   Resposta JSON: {data}')
            except:
                print(f'   Conteúdo: {checkout_response.text[:200]}')
        else:
            print(f'   ❌ Checkout falhou com status {checkout_response.status_code}')
            print(f'   Conteúdo: {checkout_response.text[:300]}')

    except Exception as e:
        print(f'❌ ERRO: {e}')

if __name__ == '__main__':
    testar_checkout()


