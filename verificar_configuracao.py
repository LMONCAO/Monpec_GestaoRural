#!/usr/bin/env python
"""Script para verificar se as configurações do Mercado Pago estão carregadas"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.conf import settings

print("=" * 60)
print("VERIFICAÇÃO DE CONFIGURAÇÃO DO MERCADO PAGO")
print("=" * 60)

# Verificar Access Token
access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
if access_token:
    print(f"✅ MERCADOPAGO_ACCESS_TOKEN: {access_token[:30]}...")
else:
    print("❌ MERCADOPAGO_ACCESS_TOKEN: NÃO CONFIGURADO")

# Verificar Public Key
public_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', '')
if public_key:
    print(f"✅ MERCADOPAGO_PUBLIC_KEY: {public_key[:30]}...")
else:
    print("❌ MERCADOPAGO_PUBLIC_KEY: NÃO CONFIGURADO")

# Verificar Gateway
gateway = getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', '')
print(f"✅ PAYMENT_GATEWAY_DEFAULT: {gateway}")

print("=" * 60)

if access_token and public_key:
    print("✅ TUDO CONFIGURADO CORRETAMENTE!")
    print("✅ O servidor deve redirecionar para o Mercado Pago agora.")
else:
    print("❌ FALTAM CONFIGURAÇÕES!")
    print("❌ Verifique o arquivo .env na raiz do projeto.")

