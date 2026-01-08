#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from decouple import config
from django.conf import settings

print("=== TESTANDO CONFIGURACOES MERCADO PAGO ===")

# Testar carregamento via decouple
try:
    token_decouple = config('MERCADOPAGO_ACCESS_TOKEN', default='')
    print("Token via decouple: {}".format("Encontrado" if token_decouple else "Nao encontrado"))
    if token_decouple:
        print("Token comeca com: {}...".format(token_decouple[:10]))
except Exception as e:
    print("Erro ao carregar token via decouple: {}".format(e))

# Testar carregamento via settings
try:
    token_settings = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
    print("Token via settings: {}".format("Encontrado" if token_settings else "Nao encontrado"))
    if token_settings:
        print("Token comeca com: {}...".format(token_settings[:10]))
except Exception as e:
    print("Erro ao carregar token via settings: {}".format(e))

# Testar import do gateway
try:
    from gestao_rural.services.payments.factory import PaymentGatewayFactory
    print("PaymentGatewayFactory importado com sucesso")

    gateway = PaymentGatewayFactory.criar_gateway('mercadopago')
    print("Gateway criado: {}".format("Sucesso" if gateway else "Falhou"))

    if gateway:
        print("Tipo do gateway: {}".format(type(gateway)))
except Exception as e:
    print("Erro ao testar gateway: {}".format(e))
    import traceback
    traceback.print_exc()

print("\n=== FIM DO TESTE ===")
