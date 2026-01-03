#!/usr/bin/env python
"""
Script para criar admin via manage.py shell
Execute: python manage.py shell < criar_admin_via_shell.py
Ou: python -c "$(cat criar_admin_via_shell.py)" manage.py shell
"""
from django.contrib.auth import get_user_model

User = get_user_model()

import os

username = 'admin'
# ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
password = os.getenv('ADMIN_PASSWORD')
if not password:
    print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
    print("   Configure a variável antes de executar:")
    print("   export ADMIN_PASSWORD='sua-senha-segura'")
    exit(1)
email = 'admin@monpec.com.br'

print("=" * 60)
print("CRIANDO/CORRIGINDO USUÁRIO ADMIN")
print("=" * 60)
print()

# Criar ou obter usuário
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

# Configurar permissões
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

print()
print("=" * 60)
print("✅ SUCESSO!")
print("=" * 60)
print(f"Username: {username}")
print(f"Password: {password}")
print()
print("Agora você pode fazer login no sistema!")






