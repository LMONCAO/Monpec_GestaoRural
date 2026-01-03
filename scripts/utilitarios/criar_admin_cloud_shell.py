#!/usr/bin/env python
"""
Script para criar admin - Execute no Cloud Shell com:
python criar_admin_cloud_shell.py

OU execute via Cloud Run Job
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model

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
print("CRIANDO/CORRIGINDO USUÁRIO ADMIN")
print("=" * 60)
print()

try:
    # Buscar ou criar usuário
    try:
        user = User.objects.get(username=username)
        print(f"✅ Usuário '{username}' encontrado")
        print(f"   - ID: {user.id}")
        print(f"   - Email: {user.email}")
        print(f"   - Ativo: {user.is_active}")
        print(f"   - Staff: {user.is_staff}")
        print(f"   - Superuser: {user.is_superuser}")
    except User.DoesNotExist:
        print(f"📝 Criando novo usuário '{username}'...")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Usuário '{username}' criado")
    
    # Configurar permissões e senha
    print()
    print("📝 Configurando permissões e senha...")
    user.set_password(password)
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
        print(f"❌ ERRO: Senha não confere")
        sys.exit(1)
    
    # Testar autenticação
    print()
    print("🔑 Testando autenticação...")
    from django.contrib.auth import authenticate
    user_auth = authenticate(username=username, password=password)
    if user_auth:
        print(f"✅ Autenticação: SUCESSO")
    else:
        print(f"⚠️  Autenticação falhou (pode ser normal em alguns ambientes)")
    
    print()
    print("=" * 60)
    print("✅ SUCESSO!")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print()
    print("Agora você pode fazer login no sistema!")
    print("URL: https://monpec-fzzfjppzva-uc.a.run.app")
    print()
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)






