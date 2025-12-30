#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir a senha de um usuário assinante em produção
Também pode criar um novo usuário se ele não existir.
Execute: python corrigir_senha_assinante.py
"""
import os
import sys
import django

# Detectar ambiente e configurar Django
# Por padrão, usar settings_windows (SQLite local) para desenvolvimento
# Se quiser usar produção, defina a variável de ambiente: DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp

# Verificar se há variável de ambiente definida
settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_windows')

# Se não estiver definida, perguntar ao usuário
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    print("=" * 60)
    print("ESCOLHA O AMBIENTE")
    print("=" * 60)
    print()
    print("1. Desenvolvimento Local (SQLite) - Recomendado para testes")
    print("2. Produção (PostgreSQL - Cloud)")
    print()
    escolha = input("Escolha (1 ou 2) [padrão: 1]: ").strip()
    
    if escolha == '2':
        settings_module = 'sistema_rural.settings_gcp'
        print("⚠️ Usando configuração de PRODUÇÃO (PostgreSQL)")
    else:
        settings_module = 'sistema_rural.settings_windows'
        print("✅ Usando configuração de DESENVOLVIMENTO (SQLite)")
    
    print()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model, authenticate
from gestao_rural.models import AssinaturaCliente

User = get_user_model()

def corrigir_senha_assinante():
    """Corrige a senha de um usuário assinante ou cria um novo usuário"""
    print("=" * 60)
    print("CORRIGIR SENHA / CRIAR USUÁRIO ASSINANTE")
    print("=" * 60)
    print()
    
    # Solicitar informações do usuário
    username_or_email = input("Digite o username ou email do assinante: ").strip()
    if not username_or_email:
        print("❌ ERRO: Username ou email não informado!")
        return False
    
    # Buscar usuário
    user = None
    if '@' in username_or_email:
        # Buscar por email
        user = User.objects.filter(email__iexact=username_or_email).first()
    else:
        # Buscar por username
        user = User.objects.filter(username__iexact=username_or_email).first()
    
    if not user:
        print(f"⚠️ Usuário '{username_or_email}' não encontrado!")
        print()
        resposta = input("Deseja criar um novo usuário? (s/n): ").strip().lower()
        if resposta != 's':
            print("Operação cancelada.")
            return False
        
        # Criar novo usuário
        print()
        print("Criando novo usuário...")
        
        # Se foi informado email, usar como email e gerar username
        if '@' in username_or_email:
            email = username_or_email.lower().strip()
            username_base = email.split('@')[0]
            username = username_base
            sufixo = 1
            # Garantir username único
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{sufixo}"
                sufixo += 1
            
            # Solicitar nome completo
            nome_completo = input("Digite o nome completo do usuário: ").strip()
            if not nome_completo:
                print("❌ ERRO: Nome completo é obrigatório!")
                return False
            
            # Criar usuário
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=nome_completo.split()[0] if nome_completo.split() else '',
                    last_name=' '.join(nome_completo.split()[1:]) if len(nome_completo.split()) > 1 else '',
                    is_active=True,
                )
                print(f"✅ Usuário criado com sucesso!")
                print(f"   - Username: {user.username}")
                print(f"   - Email: {user.email}")
            except Exception as e:
                print(f"❌ ERRO ao criar usuário: {e}")
                return False
        else:
            # Se foi informado username, solicitar email
            username = username_or_email.strip()
            email = input("Digite o email do usuário: ").strip().lower()
            if not email or '@' not in email:
                print("❌ ERRO: Email inválido!")
                return False
            
            # Verificar se email já existe
            if User.objects.filter(email__iexact=email).exists():
                print(f"❌ ERRO: Já existe um usuário com o email '{email}'!")
                return False
            
            # Solicitar nome completo
            nome_completo = input("Digite o nome completo do usuário: ").strip()
            if not nome_completo:
                print("❌ ERRO: Nome completo é obrigatório!")
                return False
            
            # Criar usuário
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=nome_completo.split()[0] if nome_completo.split() else '',
                    last_name=' '.join(nome_completo.split()[1:]) if len(nome_completo.split()) > 1 else '',
                    is_active=True,
                )
                print(f"✅ Usuário criado com sucesso!")
                print(f"   - Username: {user.username}")
                print(f"   - Email: {user.email}")
            except Exception as e:
                print(f"❌ ERRO ao criar usuário: {e}")
                return False
    
    print(f"✅ Usuário encontrado:")
    print(f"   - Username: {user.username}")
    print(f"   - Email: {user.email}")
    print(f"   - Ativo: {user.is_active}")
    print(f"   - Staff: {user.is_staff}")
    print(f"   - Superuser: {user.is_superuser}")
    
    # Verificar se é assinante
    is_assinante = False
    if user.is_superuser or user.is_staff:
        is_assinante = True
        print(f"   - Tipo: Admin/Superuser")
    else:
        assinatura = AssinaturaCliente.objects.filter(usuario=user).first()
        if assinatura:
            is_assinante = True
            print(f"   - Tipo: Assinante")
            print(f"   - Status Assinatura: {assinatura.get_status_display()}")
            print(f"   - Acesso Liberado: {assinatura.acesso_liberado}")
        else:
            print(f"   - Tipo: Usuário comum (não é assinante)")
    
    if not is_assinante:
        resposta = input("\n⚠️ Este usuário não é assinante. Deseja continuar mesmo assim? (s/n): ").strip().lower()
        if resposta != 's':
            print("Operação cancelada.")
            return False
    
    print()
    
    # Solicitar nova senha
    print("Digite a nova senha para o usuário:")
    print("(A senha será ocultada durante a digitação)")
    import getpass
    nova_senha = getpass.getpass("Nova senha: ")
    
    if not nova_senha:
        print("❌ ERRO: Senha não pode ser vazia!")
        return False
    
    confirmar_senha = getpass.getpass("Confirmar senha: ")
    
    if nova_senha != confirmar_senha:
        print("❌ ERRO: As senhas não coincidem!")
        return False
    
    # Validar senha (mínimo 12 caracteres conforme settings)
    if len(nova_senha) < 12:
        print("⚠️ AVISO: A senha tem menos de 12 caracteres. O sistema pode rejeitar.")
        resposta = input("Deseja continuar mesmo assim? (s/n): ").strip().lower()
        if resposta != 's':
            print("Operação cancelada.")
            return False
    
    # Redefinir senha
    print()
    print("Redefinindo senha...")
    try:
        user.set_password(nova_senha)
        user.save()
        print("✅ Senha redefinida com sucesso!")
    except Exception as e:
        print(f"❌ ERRO ao redefinir senha: {e}")
        return False
    
    # Testar autenticação
    print()
    print("Testando autenticação...")
    user_test = authenticate(username=user.username, password=nova_senha)
    if user_test:
        print("✅ Autenticação bem-sucedida! A senha está funcionando corretamente.")
    else:
        print("⚠️ AVISO: A autenticação falhou. Isso pode ser normal se houver validações adicionais.")
        print("   Tente fazer login no sistema para verificar.")
    
    print()
    print("=" * 60)
    print("OPERAÇÃO CONCLUÍDA")
    print("=" * 60)
    print()
    print(f"Usuário: {user.username}")
    print(f"Email: {user.email}")
    print(f"Senha: {'*' * len(nova_senha)}")
    print()
    print("✅ Você pode fazer login agora com as novas credenciais.")
    
    return True

if __name__ == '__main__':
    try:
        corrigir_senha_assinante()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

