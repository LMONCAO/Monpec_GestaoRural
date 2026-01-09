import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
import django
django.setup()
from django.contrib.auth.models import User

print('Atualizando credenciais do administrador...')

# Tentar encontrar usuário admin existente
admin_user = User.objects.filter(username='admin').first()

if admin_user:
    print(f'Encontrado usuário: {admin_user.username}')
    # Atualizar email e senha
    admin_user.email = 'admin@monpec.com.br'
    admin_user.set_password('L6171r12@@jjms')
    admin_user.save()
    print('✅ Credenciais atualizadas!')
    print(f'📧 Email: {admin_user.email}')
    print('🔑 Senha atualizada para: L6171r12@@jjms')
else:
    print('❌ Usuário admin não encontrado')
    # Criar novo superusuário
    print('Criando novo superusuário...')
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@monpec.com.br',
        password='L6171r12@@jjms',
        first_name='Administrador',
        last_name='Sistema'
    )
    print('✅ Superusuário criado!')
    print(f'👤 Usuário: {admin_user.username}')
    print(f'📧 Email: {admin_user.email}')

print('\n🎉 Credenciais prontas para uso!')
print('🌐 Acesse: https://monpec.com.br/login/')
print('📧 Email: admin@monpec.com.br')
print('🔑 Senha: L6171r12@@jjms')
