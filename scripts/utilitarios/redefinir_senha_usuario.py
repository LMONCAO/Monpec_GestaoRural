#!/usr/bin/env python
"""
Script para redefinir senha de um usuário
Uso: python redefinir_senha_usuario.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def redefinir_senha():
    """Redefine a senha do usuário Leandro"""
    email = 'l.moncaosilva@gmail.com'
    nova_senha = input(f"Digite a nova senha para {email} (ou pressione Enter para usar senha padrão 'L6171r12@@'): ").strip()
    
    if not nova_senha:
        nova_senha = 'L6171r12@@'
    
    try:
        usuario = User.objects.get(email=email)
        usuario.set_password(nova_senha)
        usuario.is_active = True  # Garantir que está ativo
        usuario.save()
        
        print(f"✅ Senha redefinida com sucesso para {email}!")
        print(f"   Username: {usuario.username}")
        print(f"   Nova senha: {nova_senha}")
        print(f"   Status: {'Ativo' if usuario.is_active else 'Inativo'}")
        return True
    except User.DoesNotExist:
        print(f"❌ Usuário com email {email} não encontrado!")
        return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == '__main__':
    print("🔐 Redefinindo senha do usuário...")
    print("")
    sucesso = redefinir_senha()
    print("")
    if sucesso:
        print("✅ Processo concluído!")
    else:
        print("❌ Falha ao redefinir senha")
        sys.exit(1)













































