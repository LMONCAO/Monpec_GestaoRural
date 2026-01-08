#!/usr/bin/env python
"""
Teste simples da API do Mercado Pago
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.conf import settings
import mercadopago

print('=== TESTE SIMPLES MERCADO PAGO ===')

# Verificar token
token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
if not token:
    print('Token nao encontrado')
    exit()

print('Token encontrado')

# Inicializar SDK
sdk = mercadopago.SDK(token)
print('SDK inicializado')

# Criar preference simples
preference_data = {
    "items": [{
        "title": "Plano Basico",
        "quantity": 1,
        "currency_id": "BRL",
        "unit_price": 99.90,
    }],
    "back_urls": {
        "success": "https://localhost:8000/assinaturas/sucesso/",
        "failure": "https://localhost:8000/assinaturas/cancelado/",
    },
    "payer": {
        "name": "Rafael",
        "email": "rafael@monpec.com.br",
    }
}

print('Enviando preference...')
response = sdk.preference().create(preference_data)

status = response.get('status')
print(f'Status: {status}')

if status == 201:
    print('Preference criada com sucesso!')
    preference = response.get('response', {})
    init_point = preference.get('init_point')
    if init_point:
        print(f'URL: {init_point}')
        print('CHECKOUT FUNCIONANDO!')
    else:
        print('URL nao encontrada')
else:
    error_msg = response.get("message", "Erro desconhecido")
    print(f'Erro: {error_msg}')
    cause = response.get('cause', [])
    if cause:
        for c in cause:
            desc = c.get("description", str(c))
            print(f'Causa: {desc}')

print('=== FIM ===')


