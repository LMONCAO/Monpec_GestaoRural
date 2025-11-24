"""
Script para limpar bloqueios de login e resetar senha do admin
"""
import os
import sys
import django

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.cache import cache

print("=" * 60)
print("LIMPANDO BLOQUEIOS DE LOGIN E RESETANDO SENHA")
print("=" * 60)
print()

# Limpar todos os bloqueios de login no cache
print("🔓 Limpando bloqueios de login...")
chaves_cache = []
# Limpar bloqueios por usuário
for i in range(100):  # Verificar até 100 chaves possíveis
    chave = f'login_attempts_user_admin_{i}'
    if cache.get(chave):
        cache.delete(chave)
        chaves_cache.append(chave)

# Limpar bloqueios padrão
chaves_padrao = [
    'login_attempts_user_admin',
    'login_blocked_user_admin',
    'login_attempts_ip_*',
]
for chave in chaves_padrao:
    cache.delete(chave)

print(f"✅ {len(chaves_cache)} bloqueio(s) removido(s)")
print()

# Resetar senha do admin
print("🔑 Resetando senha do admin...")
NOVA_SENHA = "AdminMonpec2025!@"

if User.objects.filter(username='admin').exists():
    usuario = User.objects.get(username='admin')
    usuario.set_password(NOVA_SENHA)
    usuario.is_superuser = True
    usuario.is_staff = True
    usuario.is_active = True
    if not usuario.email:
        usuario.email = 'admin@monpec.com.br'
    usuario.save()
    print('✅ Senha do usuário admin atualizada com sucesso!')
else:
    usuario = User.objects.create_superuser(
        username='admin',
        email='admin@monpec.com.br',
        password=NOVA_SENHA
    )
    print('✅ Usuário admin criado com sucesso!')

print()
print('=' * 60)
print('CREDENCIAIS DE ACESSO:')
print('=' * 60)
print('Usuário: admin')
print(f'Senha: {NOVA_SENHA}')
print('=' * 60)
print()

# Verificar se a senha está funcionando
print("🧪 Testando autenticação...")
from django.contrib.auth import authenticate
user_test = authenticate(username='admin', password=NOVA_SENHA)
if user_test:
    print("✅ Autenticação testada com sucesso!")
else:
    print("❌ ERRO: Autenticação falhou mesmo após reset!")

print()
print("✅ PROCESSO CONCLUÍDO!")
print()
print("💡 Agora você pode fazer login com:")
print(f"   Usuário: admin")
print(f"   Senha: {NOVA_SENHA}")
print()
print("⚠️  Se ainda não funcionar:")
print("   1. Limpe o cache do navegador")
print("   2. Aguarde 1 minuto (se havia bloqueio)")
print("   3. Tente fazer login novamente")

