import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.conf import settings
from gestao_rural.models import PlanoAssinatura, AssinaturaCliente

print('=== VERIFICAÇÃO DO SISTEMA DE ASSINATURAS ===')

# 1. Verificar se há planos de assinatura
planos = PlanoAssinatura.objects.all()
print(f'Planos de assinatura encontrados: {planos.count()}')
for plano in planos[:3]:
    print(f'  - {plano.nome}: R$ {plano.preco_mensal_referencia}')

# 2. Verificar assinaturas existentes
assinaturas = AssinaturaCliente.objects.all()
print(f'\nAssinaturas encontradas: {assinaturas.count()}')
for ass in assinaturas[:3]:
    print(f'  - ID {ass.id}: {ass.usuario.username} - Status: {ass.status}')

# 3. Verificar configurações críticas
token_mp = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
mp_configurado = "Sim" if token_mp else "Não"
print(f'\nMercado Pago configurado: {mp_configurado}')

# 4. Verificar webhook
from django.urls import reverse
try:
    webhook_url = reverse('mercadopago_webhook')
    print(f'Webhook configurado: Sim')
except:
    print('Webhook configurado: Não')

# 5. Verificar email
email_host = getattr(settings, 'EMAIL_HOST', '')
email_configurado = "Sim" if email_host else "Não"
print(f'Email configurado: {email_configurado}')

print('\n=== SISTEMA VERIFICADO ===')