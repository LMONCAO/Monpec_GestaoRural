#!/usr/bin/env python
"""
Teste simples da criação do gateway
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

print('Testando criacao do gateway...')

try:
    from gestao_rural.services.payments.factory import PaymentGatewayFactory
    print('Factory importada')

    gateway = PaymentGatewayFactory.criar_gateway('mercadopago')
    print(f'Gateway criado: {gateway}')
    print(f'Nome: {gateway.name}')

except Exception as e:
    print(f'Erro: {e}')
    import traceback
    traceback.print_exc()


