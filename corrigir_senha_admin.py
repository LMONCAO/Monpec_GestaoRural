"""
Script para corrigir a senha do usuário admin
Uso: python corrigir_senha_admin.py
"""
import os
import sys
import django

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User

# Senha forte que atende todos os requisitos
NOVA_SENHA = "AdminMonpec2025!@"

print("=" * 60)
print("CORRIGINDO SENHA DO ADMIN")
print("=" * 60)
print()

# Verifica se o usuário admin existe
if User.objects.filter(username='admin').exists():
    usuario = User.objects.get(username='admin')
    usuario.set_password(NOVA_SENHA)
    usuario.is_superuser = True
    usuario.is_staff = True
    usuario.is_active = True
    if not usuario.email:
        usuario.email = 'admin@monpec.com.br'
    usuario.save()
    print('[OK] Senha do usuario admin atualizada com sucesso!')
else:
    # Cria novo usuário admin
    usuario = User.objects.create_superuser(
        username='admin',
        email='admin@monpec.com.br',
        password=NOVA_SENHA
    )
    print('[OK] Usuario admin criado com sucesso!')

print()
print('=' * 60)
print('CREDENCIAIS DE ACESSO:')
print('=' * 60)
print(f'Usuário: admin')
print(f'Senha: {NOVA_SENHA}')
print('=' * 60)
print()
print('[IMPORTANTE]')
print('A senha "123456" esta bloqueada pelo sistema por questoes de seguranca.')
print('A nova senha atende a todos os requisitos de seguranca:')
print('  - Minimo 12 caracteres [OK]')
print('  - Letra maiuscula [OK]')
print('  - Letra minuscula [OK]')
print('  - Numero [OK]')
print('  - Caractere especial [OK]')
print('  - Nao contem sequencias comuns [OK]')

