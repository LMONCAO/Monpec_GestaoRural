import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()
username = 'admin'
# ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
password = os.getenv('ADMIN_PASSWORD')
if not password:
    print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
    print("   Configure a variável antes de executar:")
    print("   export ADMIN_PASSWORD='sua-senha-segura'")
    sys.exit(1)

print("=" * 60)
print("CORRIGINDO SENHA DO USUARIO ADMIN")
print("=" * 60)
print()

user, created = User.objects.get_or_create(
    username=username,
    defaults={
        'email': 'admin@monpec.com.br',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
    }
)

if created:
    print(f"Usuario '{username}' CRIADO")
else:
    print(f"Usuario '{username}' ENCONTRADO")

print(f"   - Email: {user.email}")
print(f"   - Ativo: {user.is_active}")
print(f"   - Staff: {user.is_staff}")
print(f"   - Superuser: {user.is_superuser}")
print()

print("Redefinindo senha...")
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.email = 'admin@monpec.com.br'
user.save()
print("Senha redefinida!")
print()

print("Verificando senha...")
if user.check_password(password):
    print("Senha verificada: CORRETA")
else:
    print("ERRO: Senha ainda esta incorreta")
    sys.exit(1)

print()
print("Testando autenticacao Django...")
user_auth = authenticate(username=username, password=password)
if user_auth:
    print("Autenticacao Django: SUCESSO")
    print(f"   - ID: {user_auth.id}")
    print(f"   - Username: {user_auth.username}")
else:
    print("Autenticacao Django: FALHOU")
    sys.exit(1)

print()
print("=" * 60)
print("SUCESSO! Senha corrigida e testada")
print("=" * 60)
print(f"Username: {username}")
print(f"Password: {password}")
print()
print("Agora voce pode fazer login no sistema!")






