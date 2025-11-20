"""
Script para inicializar medidas de segurança no sistema MONPEC
Execute este script após o deploy para garantir que o sistema está seguro
"""
import os
import sys
import django

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from gestao_rural.security import (
    desabilitar_usuarios_padrao,
    verificar_usuarios_inseguros,
    USUARIOS_PADRAO_PERIGOSOS
)

def main():
    print("=" * 60)
    print("🔒 INICIALIZAÇÃO DE SEGURANÇA DO SISTEMA MONPEC")
    print("=" * 60)
    print()
    
    # 1. Desabilitar usuários padrão
    print("1️⃣  Desabilitando usuários padrão perigosos...")
    desabilitados = desabilitar_usuarios_padrao()
    if desabilitados:
        print(f"   ✅ {len(desabilitados)} usuário(s) desabilitado(s): {', '.join(desabilitados)}")
    else:
        print("   ✅ Nenhum usuário padrão encontrado")
    print()
    
    # 2. Verificar problemas
    print("2️⃣  Verificando problemas de segurança...")
    problemas = verificar_usuarios_inseguros()
    if problemas:
        print(f"   ⚠️  {len(problemas)} problema(s) encontrado(s):")
        for item in problemas:
            print(f"      • {item['usuario'].username}: {', '.join(item['problemas'])}")
    else:
        print("   ✅ Nenhum problema encontrado")
    print()
    
    # 3. Listar superusuários
    print("3️⃣  Superusuários ativos:")
    superusuarios = User.objects.filter(is_superuser=True, is_active=True)
    if superusuarios.exists():
        for su in superusuarios:
            print(f"      • {su.username} ({su.email})")
    else:
        print("      ⚠️  Nenhum superusuário ativo encontrado")
    print()
    
    # 4. Verificar usuários sem senha
    print("4️⃣  Verificando usuários sem senha...")
    usuarios_sem_senha = [u for u in User.objects.filter(is_active=True) if not u.has_usable_password()]
    if usuarios_sem_senha:
        print(f"   ⚠️  {len(usuarios_sem_senha)} usuário(s) ativo(s) sem senha:")
        for u in usuarios_sem_senha:
            print(f"      • {u.username}")
    else:
        print("   ✅ Todos os usuários ativos têm senha")
    print()
    
    # 5. Recomendações
    print("=" * 60)
    print("📋 PRÓXIMOS PASSOS:")
    print("=" * 60)
    print()
    print("1. Certifique-se de que não há usuários com senhas padrão")
    print("2. Crie um superusuário seguro (se necessário):")
    print("   python manage.py createsuperuser")
    print()
    print("3. Execute a verificação completa:")
    print("   python manage.py verificar_seguranca")
    print()
    print("4. Altere o SECRET_KEY no settings.py (use variável de ambiente)")
    print("5. Configure ALLOWED_HOSTS apenas com seus domínios")
    print("6. Desabilite DEBUG em produção")
    print()
    print("=" * 60)
    print("✅ Inicialização de segurança concluída!")
    print("=" * 60)

if __name__ == '__main__':
    main()







