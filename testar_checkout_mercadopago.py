"""Script para testar a criação de checkout do Mercado Pago."""

import os
import sys
import django
from pathlib import Path

# Encontrar o diretório do projeto
script_dir = Path(__file__).resolve().parent
os.chdir(script_dir)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.conf import settings
from gestao_rural.services.payments.factory import PaymentGatewayFactory
from gestao_rural.models import PlanoAssinatura, AssinaturaCliente
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("Testando checkout do Mercado Pago")
print("=" * 60)
print()

# Verificar configurações
print("1. Verificando configuracoes...")
access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
public_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', '')
gateway_default = getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', 'mercadopago')

if not access_token:
    print("ERRO: MERCADOPAGO_ACCESS_TOKEN nao configurado!")
    print("Configure no .env: MERCADOPAGO_ACCESS_TOKEN=seu_token")
    sys.exit(1)
else:
    print(f"OK - Access Token configurado (inicia com: {access_token[:10]}...)")

if not public_key:
    print("AVISO: MERCADOPAGO_PUBLIC_KEY nao configurado (opcional)")
else:
    print(f"OK - Public Key configurado")

print(f"Gateway padrao: {gateway_default}")
print()

# Testar criação do gateway
print("2. Testando criacao do gateway...")
try:
    gateway = PaymentGatewayFactory.criar_gateway('mercadopago')
    print(f"OK - Gateway criado: {gateway.name}")
except Exception as e:
    print(f"ERRO ao criar gateway: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Buscar um plano
print()
print("3. Buscando plano de teste...")
plano = PlanoAssinatura.objects.filter(ativo=True).first()
if not plano:
    print("ERRO: Nenhum plano ativo encontrado!")
    print("Crie um plano no admin primeiro.")
    sys.exit(1)
print(f"OK - Plano encontrado: {plano.nome} (R$ {plano.preco_mensal_referencia or 0})")

# Buscar ou criar usuário de teste
print()
print("4. Buscando usuario de teste...")
usuario = User.objects.filter(is_superuser=True).first()
if not usuario:
    print("ERRO: Nenhum usuario encontrado!")
    sys.exit(1)
print(f"OK - Usuario encontrado: {usuario.username}")

# Criar assinatura de teste
print()
print("5. Criando assinatura de teste...")
assinatura, created = AssinaturaCliente.objects.get_or_create(
    usuario=usuario,
    defaults={"plano": plano}
)
assinatura.plano = plano
assinatura.status = AssinaturaCliente.Status.PENDENTE
assinatura.gateway_pagamento = 'mercadopago'
assinatura.save()
print(f"OK - Assinatura {'criada' if created else 'atualizada'}: ID {assinatura.id}")

# Testar criação de checkout
print()
print("6. Testando criacao de checkout...")
try:
    success_url = "http://localhost:8000/assinaturas/sucesso/"
    cancel_url = "http://localhost:8000/assinaturas/cancelado/"
    
    session_result = gateway.criar_checkout_session(
        assinatura=assinatura,
        plano=plano,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    
    print(f"OK - Checkout criado com sucesso!")
    print(f"   Session ID: {session_result.session_id}")
    print(f"   URL: {session_result.url}")
    print()
    print("=" * 60)
    print("SUCESSO! O checkout esta funcionando.")
    print("=" * 60)
    print()
    print("URL do checkout:")
    print(session_result.url)
    
except Exception as e:
    print(f"ERRO ao criar checkout: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)






















