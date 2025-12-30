#!/usr/bin/env python
"""
Script para criar/atualizar superusuário admin em produção
Especificamente para Cloud SQL via Cloud Shell
Execute: python criar_admin_cloud_sql.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar variáveis de ambiente antes de setup
# Obter do Cloud SQL
if not os.getenv('DB_HOST'):
    # Tentar obter do Cloud SQL
    import subprocess
    try:
        # Obter instância do Cloud SQL
        result = subprocess.run(
            ['gcloud', 'sql', 'instances', 'list', '--format', 'value(name)'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            instance_name = result.stdout.strip().split('\n')[0]
            # Obter IP público
            ip_result = subprocess.run(
                ['gcloud', 'sql', 'instances', 'describe', instance_name, '--format', 'value(ipAddresses[0].ipAddress)'],
                capture_output=True,
                text=True
            )
            if ip_result.returncode == 0 and ip_result.stdout.strip():
                os.environ['DB_HOST'] = ip_result.stdout.strip()
                print(f"✅ DB_HOST configurado para: {os.environ['DB_HOST']}")
    except Exception as e:
        print(f"⚠️  Não foi possível obter DB_HOST automaticamente: {e}")

# Definir variáveis padrão se não existirem
if not os.getenv('DB_NAME'):
    os.environ['DB_NAME'] = 'monpec_db'
if not os.getenv('DB_USER'):
    os.environ['DB_USER'] = 'monpec_user'
if not os.getenv('DB_PASSWORD'):
    print("⚠️  DB_PASSWORD não configurado. Configure via variável de ambiente.")
    print("   Execute: export DB_PASSWORD='sua_senha'")
    # Tentar obter do Secret Manager ou permitir input
    password = input("Digite a senha do banco (ou pressione Enter para tentar sem senha): ")
    if password:
        os.environ['DB_PASSWORD'] = password

django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Credenciais do admin
username = 'admin'
email = 'admin@monpec.com.br'
password = 'L6171r12@@'

print("=" * 60)
print("CRIANDO/ATUALIZANDO SUPERUSUÁRIO ADMIN")
print("=" * 60)
print()

try:
    if User.objects.filter(username=username).exists():
        usuario = User.objects.get(username=username)
        usuario.set_password(password)
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.is_active = True
        usuario.email = email
        usuario.save()
        print(f'✅ Superusuário "{username}" ATUALIZADO com sucesso!')
        print(f'   Senha alterada para: {password}')
    else:
        User.objects.create_superuser(username, email, password)
        print(f'✅ Superusuário "{username}" CRIADO com sucesso!')
    
    print()
    print('=' * 60)
    print('CREDENCIAIS DE ACESSO:')
    print('=' * 60)
    print(f'Usuário: {username}')
    print(f'Email: {email}')
    print(f'Senha: {password}')
    print('=' * 60)
    print()
    print('✅ Pronto! Você já pode fazer login em https://monpec.com.br/login/')
    print()
    
except Exception as e:
    print(f'❌ ERRO ao criar/atualizar superusuário: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)








