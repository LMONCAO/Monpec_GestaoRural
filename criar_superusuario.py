"""
Script para criar um superusuário de forma não-interativa
Execute: python311\python.exe criar_superusuario.py
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

def criar_superusuario():
    print("=" * 60)
    print("CRIACAO DE SUPERUSUARIO - SISTEMA MONPEC")
    print("=" * 60)
    print()
    
    # Solicita dados
    print("IMPORTANTE: Use um nome de usuario unico (nao 'admin' ou 'administrator')")
    print()
    
    username = input("Nome de usuário: ").strip()
    
    if not username:
        print("ERRO: Nome de usuario nao pode ser vazio!")
        return
    
    # Verifica se é um usuário padrão perigoso
    if username.lower() in [u.lower() for u in USUARIOS_PADRAO_PERIGOSOS]:
        print(f"ATENCAO: '{username}' e um nome de usuario padrao perigoso!")
        resposta = input("Deseja continuar mesmo assim? (s/N): ").strip().lower()
        if resposta != 's':
            print("ERRO: Operacao cancelada. Use um nome de usuario unico.")
            return
    
    # Verifica se já existe
    if User.objects.filter(username=username).exists():
        print(f"ERRO: O usuario '{username}' ja existe!")
        resposta = input("Deseja alterar a senha deste usuário? (s/N): ").strip().lower()
        if resposta == 's':
            usuario = User.objects.get(username=username)
            alterar_senha(usuario)
        return
    
    email = input("Email (opcional): ").strip()
    
    # Solicita senha
    print()
    print("📋 Requisitos da senha:")
    print("   - Mínimo 12 caracteres")
    print("   - Pelo menos 1 letra maiúscula")
    print("   - Pelo menos 1 letra minúscula")
    print("   - Pelo menos 1 número")
    print("   - Pelo menos 1 caractere especial (!@#$%^&*...)")
    print()
    
    while True:
        password = input("Senha: ")
        try:
            validar_senha_forte(password)
            break
        except Exception as e:
            print(f"❌ {e}")
            print("Tente novamente.\n")
    
    # Confirma senha
    password_confirm = input("Confirme a senha: ")
    if password != password_confirm:
        print("❌ As senhas não coincidem!")
        return
    
    # Cria o superusuário
    try:
        usuario = User.objects.create_superuser(
            username=username,
            email=email if email else '',
            password=password
        )
        print()
        print("=" * 60)
        print("SUCESSO: Superusuario criado com sucesso!")
        print("=" * 60)
        print(f"   Usuario: {usuario.username}")
        print(f"   Email: {usuario.email or '(nao informado)'}")
        print(f"   Superusuario: Sim")
        print(f"   Ativo: Sim")
        print()
        print("IMPORTANTE: Guarde estas informacoes em local seguro!")
        print("=" * 60)
    except Exception as e:
        print(f"ERRO ao criar superusuario: {e}")

def alterar_senha(usuario):
    print()
    print("📋 Requisitos da senha:")
    print("   - Mínimo 12 caracteres")
    print("   - Pelo menos 1 letra maiúscula")
    print("   - Pelo menos 1 letra minúscula")
    print("   - Pelo menos 1 número")
    print("   - Pelo menos 1 caractere especial (!@#$%^&*...)")
    print()
    
    while True:
        password = input("Nova senha: ")
        try:
            validar_senha_forte(password)
            break
        except Exception as e:
            print(f"❌ {e}")
            print("Tente novamente.\n")
    
    password_confirm = input("Confirme a senha: ")
    if password != password_confirm:
        print("❌ As senhas não coincidem!")
        return
    
    usuario.set_password(password)
    usuario.save()
    print()
    print("SUCESSO: Senha alterada com sucesso!")

if __name__ == '__main__':
    criar_superusuario()

