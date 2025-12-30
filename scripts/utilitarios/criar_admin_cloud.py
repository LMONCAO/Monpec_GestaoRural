#!/usr/bin/env python
"""
Script para criar usuário admin - Versão Cloud Run
Executa diretamente sem dependências de arquivos externos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
email = 'admin@monpec.com.br'
# ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
password = os.getenv('ADMIN_PASSWORD')
if not password:
    print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
    print("   Configure a variável antes de executar:")
    print("   export ADMIN_PASSWORD='sua-senha-segura'")
    exit(1)

print("🔐 Criando usuário administrador...")
print("")

try:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
    )
    
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.email = email
    user.save()
    
    if created:
        print(f"✅ Usuário admin criado com sucesso!")
    else:
        print(f"✅ Usuário admin atualizado com sucesso!")
    
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Senha: {password}")
    print("")
    print("✅ Processo concluído!")
    
except Exception as e:
    print(f"❌ Erro ao criar usuário: {e}")
    import traceback
    traceback.print_exc()
    exit(1)









