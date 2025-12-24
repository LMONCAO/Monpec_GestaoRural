#!/usr/bin/env python
"""
Script para verificar e corrigir o usuário admin
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

def verificar_admin():
    """Verifica o status do usuário admin"""
    username = 'admin'
    # ✅ SEGURANÇA: Usar variável de ambiente ao invés de senha hardcoded
    password = os.getenv('ADMIN_PASSWORD')
    if not password:
        print("⚠️  AVISO: Variável ADMIN_PASSWORD não configurada!")
        print("   O script pode falhar ao testar autenticação.")
        print("   Configure: export ADMIN_PASSWORD='sua-senha-segura'")
        password = None  # Permite continuar para verificação básica
    
    print("=" * 60)
    print("VERIFICAÇÃO DO USUÁRIO ADMIN")
    print("=" * 60)
    print()
    
    try:
        # Verificar se o usuário existe
        try:
            user = User.objects.get(username=username)
            print(f"✅ Usuário '{username}' encontrado no banco de dados")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - is_active: {user.is_active}")
            print(f"   - is_staff: {user.is_staff}")
            print(f"   - is_superuser: {user.is_superuser}")
            print(f"   - has_usable_password: {user.has_usable_password()}")
            print()
        except User.DoesNotExist:
            print(f"❌ Usuário '{username}' NÃO existe no banco de dados")
            print("   Execute: python criar_admin.py")
            return False
        
        # Verificar senha atual
        print("Testando senha atual...")
        if user.check_password(password):
            print(f"✅ Senha '{password}' está CORRETA")
        else:
            print(f"❌ Senha '{password}' está INCORRETA")
            print()
            print("Corrigindo senha...")
            user.set_password(password)
            user.save()
            print(f"✅ Senha atualizada!")
            print()
            if user.check_password(password):
                print(f"✅ Verificação: Nova senha está CORRETA")
            else:
                print(f"❌ ERRO: Nova senha ainda está INCORRETA")
        
        print()
        print("Testando autenticação completa...")
        user_auth = authenticate(username=username, password=password)
        if user_auth:
            print(f"✅ Autenticação bem-sucedida!")
        else:
            print(f"❌ Autenticação FALHOU")
            print("   Possíveis causas:")
            print("   - Senha incorreta no banco")
            print("   - Usuário inativo")
            print("   - Backend de autenticação com problema")
        
        # Verificar caracteres especiais na senha
        print()
        print("Verificando caracteres da senha...")
        print(f"   Senha original: {repr(password)}")
        print(f"   Comprimento: {len(password)}")
        print(f"   Bytes: {password.encode('utf-8')}")
        for i, char in enumerate(password):
            print(f"   [{i}] '{char}' (Unicode: {ord(char)})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    verificar_admin()






