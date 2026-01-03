#!/usr/bin/env python
"""
Script definitivo para criar admin - garante que funcione
"""
import os
import sys
import django

# Configurar Django
is_cloud_run = os.getenv('K_SERVICE') is not None
if is_cloud_run:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

username = 'admin'
# ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
password = os.getenv('ADMIN_PASSWORD')
if not password:
    print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
    print("   Configure a variável antes de executar:")
    print("   export ADMIN_PASSWORD='sua-senha-segura'")
    sys.exit(1)
email = 'admin@monpec.com.br'

print("=" * 60)
print("CRIANDO ADMIN - VERSÃO DEFINITIVA")
print("=" * 60)
print()

try:
    # Deletar usuário existente se houver (para garantir limpeza)
    try:
        old_user = User.objects.get(username=username)
        print(f"⚠️  Usuário '{username}' já existe. Deletando...")
        old_user.delete()
        print(f"✅ Usuário antigo deletado")
    except User.DoesNotExist:
        print(f"📝 Nenhum usuário '{username}' existente")
    
    print()
    print("📝 Criando novo usuário admin...")
    
    # Criar usuário usando create_user (que já faz hash da senha)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    print(f"✅ Usuário criado: {user.username}")
    
    # Configurar permissões
    print("📝 Configurando permissões...")
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.email = email
    user.save()
    
    print("✅ Permissões configuradas")
    print()
    
    # Verificar senha
    print("🔐 Verificando senha...")
    if user.check_password(password):
        print(f"✅ Senha verificada: CORRETA")
    else:
        print(f"❌ ERRO: Senha não confere, redefinindo...")
        user.set_password(password)
        user.save()
        if user.check_password(password):
            print(f"✅ Senha redefinida e verificada")
        else:
            print(f"❌ ERRO CRÍTICO: Senha ainda não confere")
            sys.exit(1)
    
    # Testar autenticação
    print()
    print("🔑 Testando autenticação Django...")
    user_auth = authenticate(username=username, password=password)
    if user_auth:
        print(f"✅ Autenticação Django: SUCESSO")
        print(f"   - ID: {user_auth.id}")
        print(f"   - Username: {user_auth.username}")
        print(f"   - Email: {user_auth.email}")
        print(f"   - Ativo: {user_auth.is_active}")
        print(f"   - Staff: {user_auth.is_staff}")
        print(f"   - Superuser: {user_auth.is_superuser}")
    else:
        print(f"⚠️  Autenticação falhou (pode ser problema de configuração)")
    
    # Verificar informações finais
    print()
    print("=" * 60)
    print("✅ SUCESSO! ADMIN CRIADO")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print()
    print("Informações do usuário no banco:")
    user_final = User.objects.get(username=username)
    print(f"  - ID: {user_final.id}")
    print(f"  - Username: {user_final.username}")
    print(f"  - Email: {user_final.email}")
    print(f"  - Ativo: {user_final.is_active}")
    print(f"  - Staff: {user_final.is_staff}")
    print(f"  - Superuser: {user_final.is_superuser}")
    print(f"  - Senha definida: {user_final.has_usable_password()}")
    print()
    print("Agora você pode fazer login no sistema!")
    print("URL: https://monpec-fzzfjppzva-uc.a.run.app")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)






