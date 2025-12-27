#!/usr/bin/env python
"""Teste rápido para verificar se o token está sendo lido"""
import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

import django
django.setup()

from django.conf import settings
from decouple import config

print("=" * 60)
print("TESTE DE CONFIGURAÇÃO DO MERCADO PAGO")
print("=" * 60)

# Teste 1: Via decouple diretamente
print("\n1. Teste via decouple (config):")
token_decouple = config('MERCADOPAGO_ACCESS_TOKEN', default='')
print(f"   Token: {'✅ ENCONTRADO' if token_decouple else '❌ NÃO ENCONTRADO'}")
if token_decouple:
    print(f"   Valor: {token_decouple[:40]}...")

# Teste 2: Via settings do Django
print("\n2. Teste via Django settings:")
token_settings = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
print(f"   Token: {'✅ ENCONTRADO' if token_settings else '❌ NÃO ENCONTRADO'}")
if token_settings:
    print(f"   Valor: {token_settings[:40]}...")

# Teste 3: Verificar arquivo .env
print("\n3. Verificando arquivo .env:")
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"   Caminho: {env_path}")
print(f"   Existe: {'✅ SIM' if os.path.exists(env_path) else '❌ NÃO'}")

if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'MERCADOPAGO_ACCESS_TOKEN' in content:
            print("   ✅ MERCADOPAGO_ACCESS_TOKEN encontrado no arquivo")
        else:
            print("   ❌ MERCADOPAGO_ACCESS_TOKEN NÃO encontrado no arquivo")

print("\n" + "=" * 60)
if token_settings:
    print("✅ CONFIGURAÇÃO OK - O servidor deve funcionar!")
else:
    print("❌ PROBLEMA - Token não está sendo lido pelo Django")
    print("   Tente reiniciar o servidor manualmente")
print("=" * 60)

