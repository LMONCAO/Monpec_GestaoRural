#!/usr/bin/env python
"""
Script para redefinir a senha do usuário admin
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

def redefinir_senha_admin():
    """Redefine a senha do usuário admin e testa"""
    username = 'admin'
    # ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
    password = os.getenv('ADMIN_PASSWORD')
    if not password:
        print("❌ ERRO: Variável de ambiente ADMIN_PASSWORD não configurada!")
        print("   Configure a variável antes de executar:")
        print("   export ADMIN_PASSWORD='sua-senha-segura'")
        return False
    
    print("=" * 60)
    print("REDEFININDO SENHA DO USUÁRIO ADMIN")
    print("=" * 60)
    print()
    
    try:
        # Buscar usuário
        try:
            user = User.objects.get(username=username)
            print(f"✅ Usuário '{username}' encontrado")
            print(f"   - Email: {user.email}")
            print(f"   - Ativo: {user.is_active}")
            print(f"   - Staff: {user.is_staff}")
            print(f"   - Superuser: {user.is_superuser}")
            print()
        except User.DoesNotExist:
            print(f"❌ Usuário '{username}' não encontrado")
            print("   Criando usuário...")
            user = User.objects.create_user(
                username=username,
                email='admin@monpec.com.br',
                password=password,
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            print(f"✅ Usuário criado!")
            print()
        
        # Testar senha atual
        print("Testando senha atual...")
        if user.check_password(password):
            print(f"✅ Senha atual está CORRETA")
        else:
            print(f"❌ Senha atual está INCORRETA - Redefinindo...")
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            print(f"✅ Senha redefinida!")
        
        # Verificar novamente
        print()
        print("Verificando senha após redefinição...")
        if user.check_password(password):
            print(f"✅ Senha está CORRETA após redefinição")
        else:
            print(f"❌ ERRO: Senha ainda está incorreta após redefinição")
            return False
        
        # Testar autenticação completa
        print()
        print("Testando autenticação Django completa...")
        user_auth = authenticate(username=username, password=password)
        if user_auth:
            print(f"✅ Autenticação Django bem-sucedida!")
            print(f"   - ID: {user_auth.id}")
            print(f"   - Username: {user_auth.username}")
            return True
        else:
            print(f"❌ Autenticação Django FALHOU")
            print("   Isso pode indicar um problema com o backend de autenticação")
            return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    sucesso = redefinir_senha_admin()
    sys.exit(0 if sucesso else 1)






