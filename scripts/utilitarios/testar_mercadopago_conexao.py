#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar a conexão com o Mercado Pago
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.conf import settings
import mercadopago

print("=== TESTE DE CONEXÃO MERCADO PAGO ===\n")

# Verificar credenciais
access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
public_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', '')

print(f"ACCESS_TOKEN configurado: {'SIM' if access_token else 'NAO'}")
if access_token:
    print(f"ACCESS_TOKEN: {access_token[:20]}...")
else:
    print("ERRO: MERCADOPAGO_ACCESS_TOKEN nao configurado!")
    sys.exit(1)

print(f"PUBLIC_KEY configurado: {'SIM' if public_key else 'NAO'}")
if public_key:
    print(f"PUBLIC_KEY: {public_key[:20]}...")

# Testar SDK
try:
    print("\n=== Testando SDK do Mercado Pago ===")
    mp = mercadopago.SDK(access_token)
    print("SDK criado com sucesso!")
    
    # Testar criação de preferência simples
    print("\n=== Testando criacao de preferencia ===")
    preference_data = {
        "items": [
            {
                "title": "Teste MONPEC",
                "description": "Teste de integracao",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 137.90,
            }
        ],
        "back_urls": {
            "success": "http://localhost:8000/assinaturas/sucesso/",
            "failure": "http://localhost:8000/assinaturas/cancelado/",
            "pending": "http://localhost:8000/assinaturas/sucesso/",
        },
    }
    
    print("Dados da preferencia:", preference_data)
    response = mp.preference().create(preference_data)
    
    print(f"\nStatus da resposta: {response.get('status')}")
    print(f"Resposta completa: {response}")
    
    if response.get("status") in [200, 201]:
        preference = response.get("response", {})
        checkout_url = (
            preference.get("init_point") or 
            preference.get("sandbox_init_point") or
            preference.get("checkout_url") or 
            preference.get("url")
        )
        
        if checkout_url:
            print(f"\nSUCESSO! URL de checkout: {checkout_url}")
        else:
            print(f"\nERRO: URL de checkout nao encontrada na resposta")
            print(f"Preferencia: {preference}")
    else:
        print(f"\nERRO: Status {response.get('status')}")
        print(f"Mensagem: {response.get('message')}")
        print(f"Causa: {response.get('cause')}")
        
except Exception as e:
    print(f"\nERRO ao testar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== TESTE CONCLUIDO ===")

