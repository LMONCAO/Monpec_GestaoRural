#!/usr/bin/env python
"""
Script para criar usuário administrador no sistema MONPEC
Uso: python criar_admin.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from gestao_rural.models import AssinaturaCliente, TenantUsuario, PlanoAssinatura

User = get_user_model()

def criar_admin():
    """Cria ou atualiza usuário administrador com assinatura e perfil de tenant"""
    username = 'admin'
    email = 'admin@monpec.com.br'
    # ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
    password = os.getenv('ADMIN_PASSWORD')
    if not password:
        print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
        print("   Configure a variável antes de executar:")
        print("   export ADMIN_PASSWORD='sua-senha-segura'")
        return False
    
    try:
        # 1. Criar ou atualizar usuário
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        
        if not created:
            # Atualizar senha e permissões
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.email = email
            user.save()
            print(f"✅ Usuário admin atualizado!")
        else:
            user.set_password(password)
            user.save()
            print(f"✅ Usuário admin criado!")
        
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Senha: {password}")
        
        # 2. Criar ou obter plano padrão
        plano, plano_created = PlanoAssinatura.objects.get_or_create(
            slug='plano-admin',
            defaults={
                'nome': 'Plano Administrador',
                'descricao': 'Plano padrão para administradores do sistema',
                'stripe_price_id': 'admin_plano',
                'max_usuarios': 999,
                'ativo': True,
            }
        )
        if plano_created:
            print(f"✅ Plano padrão criado!")
        
        # 3. Criar ou atualizar assinatura
        assinatura, assinatura_created = AssinaturaCliente.objects.get_or_create(
            usuario=user,
            defaults={
                'plano': plano,
                'status': AssinaturaCliente.Status.ATIVA,
            }
        )
        
        if not assinatura_created:
            # Atualizar assinatura existente
            assinatura.plano = plano
            assinatura.status = AssinaturaCliente.Status.ATIVA
            assinatura.save()
            print(f"✅ Assinatura atualizada!")
        else:
            print(f"✅ Assinatura criada!")
        
        # 4. Garantir que o TenantUsuario existe com perfil ADMIN
        tenant_usuario, tenant_created = TenantUsuario.objects.get_or_create(
            usuario=user,
            defaults={
                'assinatura': assinatura,
                'nome_exibicao': user.get_full_name() or user.username,
                'email': user.email or email,
                'perfil': TenantUsuario.Perfil.ADMIN,
                'ativo': True,
            }
        )
        
        if not tenant_created:
            # Atualizar perfil para ADMIN se não for
            if tenant_usuario.perfil != TenantUsuario.Perfil.ADMIN:
                tenant_usuario.perfil = TenantUsuario.Perfil.ADMIN
                tenant_usuario.ativo = True
                tenant_usuario.save()
                print(f"✅ Perfil de tenant atualizado para ADMIN!")
            else:
                print(f"✅ Perfil de tenant já está como ADMIN!")
        else:
            print(f"✅ Perfil de tenant criado como ADMIN!")
        
        print(f"\n✅ Usuário admin configurado completamente!")
        print(f"   - Usuário: {username}")
        print(f"   - Assinatura: {assinatura.id} (Status: {assinatura.get_status_display()})")
        print(f"   - Perfil Tenant: {tenant_usuario.get_perfil_display()}")
        
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
    print("🔐 Criando usuário administrador...")
    print("")
    sucesso = criar_admin()
    print("")
    if sucesso:
        print("✅ Processo concluído!")
    else:
        print("❌ Falha ao criar usuário admin")
        sys.exit(1)

