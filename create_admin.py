import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
import django
django.setup()
from django.contrib.auth.models import User

print('Verificando superusuários...')
superusers = User.objects.filter(is_superuser=True)
print(f'Encontrados {superusers.count()} superusuários')

for u in superusers:
    print(f'- {u.username} ({u.email})')

if not superusers.exists():
    print('Criando superusuário admin...')
    admin = User.objects.create_superuser('admin', 'admin@monpec.com.br', 'admin123')
    admin.first_name = 'Administrador'
    admin.last_name = 'Sistema'
    admin.save()
    print('Superusuário criado!')
    print('Usuário: admin')
    print('Senha: admin123')
else:
    print('Já existe superusuário')
