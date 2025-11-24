import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 60)
print("ALTERAR SENHA DO USUARIO ADMIN")
print("=" * 60)
print()

# Buscar usuário admin
try:
    usuario = User.objects.get(username='admin')
except User.DoesNotExist:
    print("ERRO: Usuario 'admin' nao encontrado!")
    sys.exit(1)

print(f"Usuario encontrado: {usuario.username}")
print(f"Email: {usuario.email or '(sem email)'}")
print()

# Verificar se a senha foi passada como argumento
if len(sys.argv) > 1:
    nova_senha = sys.argv[1]
    if len(nova_senha) < 8:
        print("ERRO: A senha deve ter no minimo 8 caracteres!")
        sys.exit(1)
else:
    # Solicitar nova senha via input
    print("Digite a nova senha (minimo 8 caracteres):")
    nova_senha = input("Nova senha: ").strip()
    
    if len(nova_senha) < 8:
        print("ERRO: A senha deve ter no minimo 8 caracteres!")
        sys.exit(1)
    
    confirmar = input("Confirme a senha: ").strip()
    
    if nova_senha != confirmar:
        print("ERRO: As senhas nao coincidem!")
        sys.exit(1)

# Alterar senha
usuario.set_password(nova_senha)
usuario.save()

print()
print("=" * 60)
print("SENHA ALTERADA COM SUCESSO!")
print("=" * 60)
print(f"Usuario: {usuario.username}")
print(f"Email: {usuario.email or '(sem email)'}")
print()
print("Voce pode fazer login agora com a nova senha.")
print()
print("Exemplo de uso:")
print("  python alterar_senha_admin.py")
print("  ou")
print("  python alterar_senha_admin.py SuaNovaSenha123")
