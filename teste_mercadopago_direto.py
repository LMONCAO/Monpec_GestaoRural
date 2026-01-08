#!/usr/bin/env python
"""
Teste direto da API do Mercado Pago para identificar o erro 500
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.conf import settings
import mercadopago

print('=== TESTE DIRETO MERCADO PAGO ===')

# Verificar token
token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
if not token:
    print('❌ Token não encontrado')
    exit()

print('Token encontrado')

# Inicializar SDK
sdk = mercadopago.SDK(token)
print('SDK inicializado')

# Criar preference idêntica à que a view usa
preference_data = {
    "items": [
        {
            "title": "Plano Básico",
            "description": "Plano básico para pequenos produtores",
            "quantity": 1,
            "currency_id": "BRL",
            "unit_price": 99.90,
        }
    ],
    "back_urls": {
        "success": "https://localhost:8000/assinaturas/sucesso/",
        "failure": "https://localhost:8000/assinaturas/cancelado/",
        "pending": "https://localhost:8000/assinaturas/sucesso/",
    },
    "payer": {
        "name": "Rafael",
        "email": "rafael@monpec.com.br",
    },
    "payment_methods": {
        "excluded_payment_types": [],
        "excluded_payment_methods": [],
        "installments": 12,
    },
    "notification_url": "https://localhost:8000/assinaturas/webhook/mercadopago/",
    "statement_descriptor": "MONPEC ASSINATURA",
    "external_reference": "teste-123",
    "metadata": {
        "assinatura_id": "teste-123",
        "usuario_id": "1",
        "plano_slug": "basico",
        "nome_cliente": "Rafael",
        "email_cliente": "rafael@monpec.com.br",
    },
}

print('📤 Enviando preference para Mercado Pago...')
response = sdk.preference().create(preference_data)

status = response.get('status')
print(f'Status da resposta: {status}')

if status == 201:
    print('✅ Preference criada com sucesso!')
    preference = response.get('response', {})
    init_point = preference.get('init_point') or preference.get('sandbox_init_point')
    if init_point:
        print(f'URL de checkout: {init_point}')
        print('🎉 CHECKOUT FUNCIONANDO!')
    else:
        print('❌ URL de checkout não encontrada')
elif status == 400:
    print('❌ Erro 400 - Dados inválidos')
    cause = response.get('cause', [])
    if cause:
        print('Causas do erro:')
        for c in cause:
            print(f'  - {c.get("description", str(c))}')
    else:
        print(f'Resposta: {response}')
elif status == 401:
    print('❌ Erro 401 - Token inválido ou expirado')
else:
    print(f'❌ Erro {status}: {response.get("message", "Erro desconhecido")}')

print('=== FIM DO TESTE ===')
