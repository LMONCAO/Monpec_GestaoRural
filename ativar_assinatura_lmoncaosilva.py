import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import AssinaturaCliente
from django.contrib.auth.models import User

# Buscar usuário l.moncaosilva
usuario = User.objects.filter(username='l.moncaosilva').first()
if not usuario:
    print('❌ Usuário l.moncaosilva não encontrado')
    exit()

print(f'✅ Usuário encontrado: {usuario.username} ({usuario.email})')

# Buscar assinatura do usuário
assinatura = AssinaturaCliente.objects.filter(usuario=usuario).first()
if not assinatura:
    print('❌ Assinatura não encontrada para este usuário')
    exit()

print(f'📋 Status atual: {assinatura.status}')
print(f'📋 Plano: {assinatura.plano.nome if assinatura.plano else "N/A"}')
print(f'📋 Data criação: {assinatura.criado_em}')

# Alterar status para ATIVA
assinatura.status = 'ATIVA'
assinatura.data_liberacao = assinatura.criado_em.date()  # Define data de liberação como hoje
assinatura.save()

print('')
print('✅ ASSINATURA ATIVADA COM SUCESSO!')
print(f'📋 Novo status: {assinatura.status}')
print(f'📋 Data liberação: {assinatura.data_liberacao}')