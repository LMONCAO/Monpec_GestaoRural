#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar usuário administrador no sistema MONPEC
Uso: python criar_usuario_admin.py

Este script cria ou atualiza um usuário admin com todas as permissões necessárias.
"""
import os
import sys
import django
import getpass

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

def criar_admin():
    """Cria ou atualiza usuário administrador"""
    
    print("=" * 60)
    print("CRIAR USUÁRIO ADMINISTRADOR - SISTEMA MONPEC")
    print("=" * 60)
    print()
    
    # Solicitar dados do usuário
    username = input("Digite o username (ou pressione Enter para 'admin'): ").strip() or 'admin'
    email = input("Digite o email (ou pressione Enter para 'admin@monpec.com.br'): ").strip() or 'admin@monpec.com.br'
    
    # Solicitar senha de forma segura
    print()
    print("⚠️  A senha deve ter no mínimo 12 caracteres (conforme configuração do sistema)")
    password = getpass.getpass("Digite a senha: ")
    
    if len(password) < 12:
        print("❌ ERRO: A senha deve ter no mínimo 12 caracteres!")
        return False
    
    password_confirm = getpass.getpass("Confirme a senha: ")
    
    if password != password_confirm:
        print("❌ ERRO: As senhas não coincidem!")
        return False
    
    print()
    print("Criando/atualizando usuário...")
    print()
    
    try:
        # Verificar se o usuário já existe
        try:
            user = User.objects.get(username=username)
            print(f"✅ Usuário '{username}' encontrado. Atualizando...")
            user_existia = True
        except User.DoesNotExist:
            print(f"📝 Criando novo usuário '{username}'...")
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user_existia = False
        
        # Configurar permissões de admin
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.email = email
        user.save()
        
        print()
        print("=" * 60)
        print("✅ SUCESSO!")
        print("=" * 60)
        print()
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Ativo: {user.is_active}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")
        print()
        
        # Verificar se precisa criar assinatura e tenant
        try:
            from gestao_rural.models import AssinaturaCliente, TenantUsuario, PlanoAssinatura
            
            # Criar ou obter plano padrão
            plano, _ = PlanoAssinatura.objects.get_or_create(
                slug='plano-admin',
                defaults={
                    'nome': 'Plano Administrador',
                    'descricao': 'Plano padrão para administradores do sistema',
                    'stripe_price_id': 'admin_plano',
                    'max_usuarios': 999,
                    'ativo': True,
                }
            )
            
            # Criar ou atualizar assinatura
            assinatura, _ = AssinaturaCliente.objects.get_or_create(
                usuario=user,
                defaults={
                    'plano': plano,
                    'status': AssinaturaCliente.Status.ATIVA,
                }
            )
            
            # Garantir que o TenantUsuario existe com perfil ADMIN
            tenant_usuario, _ = TenantUsuario.objects.get_or_create(
                usuario=user,
                defaults={
                    'assinatura': assinatura,
                    'nome_exibicao': user.get_full_name() or user.username,
                    'email': user.email or email,
                    'perfil': TenantUsuario.Perfil.ADMIN,
                    'ativo': True,
                }
            )
            
            if tenant_usuario.perfil != TenantUsuario.Perfil.ADMIN:
                tenant_usuario.perfil = TenantUsuario.Perfil.ADMIN
                tenant_usuario.ativo = True
                tenant_usuario.save()
            
            print("✅ Assinatura e perfil de tenant configurados!")
            print()
            
        except ImportError:
            print("⚠️  Módulos de assinatura não encontrados. Usuário criado apenas como superuser.")
        except Exception as e:
            print(f"⚠️  Aviso ao configurar assinatura: {e}")
            print("   O usuário foi criado como superuser, mas pode precisar de configuração adicional.")
        
        print()
        print("=" * 60)
        print("✅ USUÁRIO ADMIN CRIADO COM SUCESSO!")
        print("=" * 60)
        print()
        print(f"Agora você pode fazer login com:")
        print(f"   Username: {username}")
        print(f"   Senha: {'*' * len(password)}")
        print()
        
        return True
        
    except ValidationError as e:
        print(f"❌ Erro de validação: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        sucesso = criar_admin()
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário.")
        sys.exit(1)

