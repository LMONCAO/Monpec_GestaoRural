import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Criar cliente de teste
client = Client()

# Criar usuário admin para teste
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    client.force_login(admin_user)

    # Fazer requisição para a página
    response = client.get('/gestao/usuarios-assinantes/')
    print(f'Status Code: {response.status_code}')

    if response.status_code == 200:
        print('✅ Página acessível com sucesso!')
        content = response.content.decode('utf-8')
        print('Conteúdo contém "Usuários Assinantes":', 'Usuários Assinantes' in content)
        print('Primeiras 200 caracteres do conteúdo:')
        print(content[:200])
    else:
        print(f'❌ Erro na página: {response.status_code}')
        print('Conteúdo do erro:')
        print(response.content.decode('utf-8')[:500])
else:
    print('❌ Usuário admin não encontrado')

    # Listar usuários disponíveis
    print('Usuários no sistema:')
    for user in User.objects.all():
        print(f'  - {user.username}: {user.email} (superuser: {user.is_superuser})')