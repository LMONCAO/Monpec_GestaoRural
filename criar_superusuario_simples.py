"""
Script para criar superusuario via linha de comando
Uso: python311\python.exe criar_superusuario_simples.py usuario email senha
"""
import os
import sys
import django

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from gestao_rural.security import validar_senha_forte, USUARIOS_PADRAO_PERIGOSOS

def criar_superusuario(username, email, password):
    print("=" * 60)
    print("CRIACAO DE SUPERUSUARIO - SISTEMA MONPEC")
    print("=" * 60)
    print()
    
    # Valida username
    if not username:
        print("ERRO: Nome de usuario nao pode ser vazio!")
        return False
    
    if username.lower() in [u.lower() for u in USUARIOS_PADRAO_PERIGOSOS]:
        print(f"ATENCAO: '{username}' e um nome de usuario padrao perigoso!")
        print("Recomendamos usar um nome unico.")
    
    # Valida senha
    try:
        validar_senha_forte(password)
    except Exception as e:
        print(f"ERRO na senha: {e}")
        return False
    
    # Verifica se ja existe
    if User.objects.filter(username=username).exists():
        print(f"O usuario '{username}' ja existe. Atualizando...")
        usuario = User.objects.get(username=username)
        usuario.set_password(password)
        usuario.email = email
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.is_active = True
        usuario.save()
        print("SUCESSO: Usuario atualizado!")
    else:
        # Cria novo
        usuario = User.objects.create_superuser(
            username=username,
            email=email if email else '',
            password=password
        )
        print("SUCESSO: Superusuario criado!")
    
    print()
    print("=" * 60)
    print("DADOS DO USUARIO:")
    print("=" * 60)
    print(f"Usuario: {usuario.username}")
    print(f"Email: {usuario.email or '(nao informado)'}")
    print(f"Superusuario: Sim")
    print(f"Ativo: Sim")
    print("=" * 60)
    return True

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("USO: python311\\python.exe criar_superusuario_simples.py <usuario> <email> <senha>")
        print()
        print("EXEMPLO:")
        print('  python311\\python.exe criar_superusuario_simples.py "joao" "joao@email.com" "MinhaSenh@Forte123"')
        print()
        print("REQUISITOS DA SENHA:")
        print("  - Minimo 12 caracteres")
        print("  - Pelo menos 1 letra maiuscula")
        print("  - Pelo menos 1 letra minuscula")
        print("  - Pelo menos 1 numero")
        print("  - Pelo menos 1 caractere especial (!@#$%^&*...)")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    criar_superusuario(username, email, password)






