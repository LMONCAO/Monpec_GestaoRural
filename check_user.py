import os
import django
import sys

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import User, AssinaturaCliente
from gestao_rural.models_auditoria import UsuarioAtivo

# Procurar usuário por email
user = User.objects.filter(email='l.moncaosilva@gmail.com').first()

if user:
    print(f'Usuário encontrado: {user.username}')
    print(f'Email: {user.email}')
    print(f'Superuser: {user.is_superuser}')
    print(f'Staff: {user.is_staff}')

    # Verificar se tem UsuarioAtivo
    has_usuario_ativo = UsuarioAtivo.objects.filter(usuario=user).exists()
    print(f'Tem UsuarioAtivo (demo): {has_usuario_ativo}')

    # Verificar assinatura
    assinatura = AssinaturaCliente.objects.filter(usuario=user).first()
    if assinatura:
        print(f'Tem assinatura: {assinatura.status}')
        print(f'Data liberação: {getattr(assinatura, "data_liberacao", None)}')
        print(f'ID assinatura: {assinatura.id}')
    else:
        print('Não tem assinatura ativa')

else:
    print('Usuário não encontrado')