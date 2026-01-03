#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script rápido para corrigir senha de assinante
Uso: python corrigir_senha_assinante_rapido.py username senha
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

def main():
    if len(sys.argv) < 3:
        print("Uso: python corrigir_senha_assinante_rapido.py <username_ou_email> <nova_senha>")
        print("Exemplo: python corrigir_senha_assinante_rapido.py admin L6171r12@@")
        sys.exit(1)
    
    username_or_email = sys.argv[1]
    nova_senha = sys.argv[2]
    
    # Buscar usuário
    user = None
    if '@' in username_or_email:
        user = User.objects.filter(email__iexact=username_or_email).first()
    else:
        user = User.objects.filter(username__iexact=username_or_email).first()
    
    if not user:
        print(f"❌ Usuário '{username_or_email}' não encontrado!")
        sys.exit(1)
    
    # Redefinir senha
    user.set_password(nova_senha)
    user.save()
    
    # Testar autenticação
    user_test = authenticate(username=user.username, password=nova_senha)
    if user_test:
        print(f"✅ Senha corrigida e testada com sucesso para '{user.username}'!")
    else:
        print(f"⚠️ Senha redefinida, mas autenticação falhou. Tente fazer login no sistema.")
    
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")

if __name__ == '__main__':
    main()


