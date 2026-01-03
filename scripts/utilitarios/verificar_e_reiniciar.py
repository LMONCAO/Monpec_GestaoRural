#!/usr/bin/env python
"""Script para verificar configuração e reiniciar servidor"""
import os
import sys
import subprocess

print("=" * 60)
print("VERIFICAÇÃO E REINÍCIO DO SERVIDOR DJANGO")
print("=" * 60)

# Verificar arquivo .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"\n1. Verificando arquivo .env:")
print(f"   Caminho: {env_path}")
print(f"   Existe: {'✅ SIM' if os.path.exists(env_path) else '❌ NÃO'}")

if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'MERCADOPAGO_ACCESS_TOKEN=APP_USR' in content:
            print("   ✅ MERCADOPAGO_ACCESS_TOKEN encontrado")
        else:
            print("   ❌ MERCADOPAGO_ACCESS_TOKEN NÃO encontrado ou inválido")
        
        if 'MERCADOPAGO_PUBLIC_KEY=APP_USR' in content:
            print("   ✅ MERCADOPAGO_PUBLIC_KEY encontrado")
        else:
            print("   ❌ MERCADOPAGO_PUBLIC_KEY NÃO encontrado ou inválido")

# Testar leitura via decouple
print(f"\n2. Testando leitura via decouple:")
try:
    from decouple import config
    token = config('MERCADOPAGO_ACCESS_TOKEN', default='')
    if token:
        print(f"   ✅ Token lido: {token[:30]}...")
    else:
        print("   ❌ Token NÃO foi lido")
except Exception as e:
    print(f"   ❌ Erro ao ler: {e}")

print("\n" + "=" * 60)
print("INSTRUÇÕES:")
print("=" * 60)
print("1. Pare o servidor Django (Ctrl+C no terminal)")
print("2. Execute: python manage.py runserver")
print("3. Teste acessando: http://localhost:8000/assinaturas/")
print("=" * 60)








