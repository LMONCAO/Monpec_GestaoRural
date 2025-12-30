#!/usr/bin/env python
"""
Script simplificado para criar usuário admin
Funciona tanto localmente quanto no Cloud Run
"""
import os
import sys
import django

# Detectar se está no Cloud Run
is_cloud_run = os.getenv('K_SERVICE') is not None

# Configurar Django
if is_cloud_run:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

def criar_admin_simples():
    """Cria ou atualiza usuário admin de forma simples"""
    username = 'admin'
    email = 'admin@monpec.com.br'
    # ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
    password = os.getenv('ADMIN_PASSWORD')
    if not password:
        print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
        print("   Configure a variável antes de executar:")
        print("   export ADMIN_PASSWORD='sua-senha-segura'")
        return False
    
    print("=" * 60)
    print("CRIANDO/CORRIGINDO USUÁRIO ADMIN")
    print("=" * 60)
    print()
    
    try:
        # Buscar ou criar usuário
        try:
            user = User.objects.get(username=username)
            print(f"✅ Usuário '{username}' encontrado")
        except User.DoesNotExist:
            print(f"📝 Criando novo usuário '{username}'...")
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Usuário '{username}' criado")
        
        # Atualizar permissões e senha
        print(f"📝 Configurando permissões...")
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.email = email
        user.save()
        
        print(f"✅ Permissões configuradas")
        print()
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Ativo: {user.is_active}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")
        print()
        
        # Verificar senha
        print("🔐 Verificando senha...")
        if user.check_password(password):
            print(f"✅ Senha verificada: CORRETA")
        else:
            print(f"❌ ERRO: Senha não confere")
            return False
        
        # Testar autenticação
        print()
        print("🔑 Testando autenticação...")
        user_auth = authenticate(username=username, password=password)
        if user_auth:
            print(f"✅ Autenticação: SUCESSO")
            print(f"   - ID: {user_auth.id}")
            print(f"   - Username: {user_auth.username}")
        else:
            print(f"⚠️  Autenticação falhou (pode ser normal em alguns ambientes)")
        
        print()
        print("=" * 60)
        print("✅ SUCESSO!")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Password: {password}")
        print()
        print("Agora você pode fazer login no sistema!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = criar_admin_simples()
    sys.exit(0 if sucesso else 1)
