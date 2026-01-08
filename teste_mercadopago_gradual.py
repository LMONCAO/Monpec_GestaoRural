import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema_rural.settings'
import django
django.setup()

from django.conf import settings
import mercadopago

print('Teste Mercado Pago - Adicionando campos gradualmente')

token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
if not token:
    print('Token não encontrado')
    exit()

sdk = mercadopago.SDK(token)

# Teste 1: Básico
print('\n1. Preference básica:')
preference_data = {
    'items': [{
        'title': 'Teste Monpec',
        'quantity': 1,
        'currency_id': 'BRL',
        'unit_price': 99.90
    }]
}

response = sdk.preference().create(preference_data)
print(f'Status: {response.get("status")}')
if response.get('status') != 201:
    print(f'ERRO: {response.get("message")}')

# Teste 2: Com back_urls
print('\n2. Adicionando back_urls:')
preference_data['back_urls'] = {
    'success': 'https://localhost:8000/assinaturas/sucesso/',
    'failure': 'https://localhost:8000/assinaturas/cancelado/',
    'pending': 'https://localhost:8000/assinaturas/sucesso/'
}

response = sdk.preference().create(preference_data)
print(f'Status: {response.get("status")}')
if response.get('status') != 201:
    print(f'ERRO: {response.get("message")}')
    cause = response.get('cause', [])
    if cause:
        for c in cause:
            print(f'  Causa: {c.get("description", str(c))}')

# Teste 3: Com payer
print('\n3. Adicionando payer:')
preference_data['payer'] = {
    'name': 'Rafael Teste',
    'email': 'rafael@monpec.com.br'
}

response = sdk.preference().create(preference_data)
print(f'Status: {response.get("status")}')
if response.get('status') != 201:
    print(f'ERRO: {response.get("message")}')
    cause = response.get('cause', [])
    if cause:
        for c in cause:
            print(f'  Causa: {c.get("description", str(c))}')

# Teste 4: Com notification_url
print('\n4. Adicionando notification_url:')
preference_data['notification_url'] = 'https://localhost:8000/assinaturas/webhook/mercadopago/'

response = sdk.preference().create(preference_data)
print(f'Status: {response.get("status")}')
if response.get('status') != 201:
    print(f'ERRO: {response.get("message")}')
    cause = response.get('cause', [])
    if cause:
        for c in cause:
            print(f'  Causa: {c.get("description", str(c))}')

# Teste 5: Com payment_methods
print('\n5. Adicionando payment_methods:')
preference_data['payment_methods'] = {
    'excluded_payment_types': [],
    'excluded_payment_methods': [],
    'installments': 12
}

response = sdk.preference().create(preference_data)
print(f'Status: {response.get("status")}')
if response.get('status') != 201:
    print(f'ERRO: {response.get("message")}')
    cause = response.get('cause', [])
    if cause:
        for c in cause:
            print(f'  Causa: {c.get("description", str(c))}')

# Teste 6: Com metadata e external_reference
print('\n6. Adicionando metadata e external_reference:')
preference_data['metadata'] = {
    'assinatura_id': 'teste-123',
    'usuario_id': '1',
    'plano_slug': 'basico'
}
preference_data['external_reference'] = 'teste-123'
preference_data['statement_descriptor'] = 'MONPEC ASSINATURA'

response = sdk.preference().create(preference_data)
print(f'Status: {response.get("status")}')
if response.get('status') != 201:
    print(f'ERRO: {response.get("message")}')
    cause = response.get('cause', [])
    if cause:
        for c in cause:
            print(f'  Causa: {c.get("description", str(c))}')

print('\n=== Teste concluído ===')
