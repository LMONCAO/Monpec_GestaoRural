#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, ProdutorRural
from django.contrib.auth import get_user_model
from gestao_rural.helpers_acesso import is_usuario_demo

User = get_user_model()

# Verificar usuário testando2 que apareceu como demo
user = User.objects.get(username='testando2')
print(f'Usuário: {user.username}')
print(f'Is demo: {is_usuario_demo(user)}')

# Verificar propriedades
propriedades = Propriedade.objects.filter(produtor__usuario_responsavel=user)
print(f'Propriedades: {list(propriedades.values_list("nome_propriedade", flat=True))}')

print('\n--- Testando Fazenda Demonstração ---')
# Encontrar a Fazenda Demonstração
propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
if propriedade:
    produtor = propriedade.produtor
    usuario = produtor.usuario_responsavel

    print(f'Usuário: {usuario}')
    print(f'Username: {usuario.username}')
    print(f'Is demo: {is_usuario_demo(usuario)}')

    # Testar função completa
    print(f'is_usuario_demo result: {is_usuario_demo(usuario)}')
else:
    print('Fazenda Demonstração não encontrada')
