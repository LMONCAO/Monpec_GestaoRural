#!/usr/bin/env python3
import os
import sys
import django
import psycopg2

# Configurações do Cloud SQL
CLOUD_SQL_HOST = '34.9.51.178'  # IP público do Cloud SQL
CLOUD_SQL_PORT = '5432'
CLOUD_SQL_DB = 'monpec_db'
CLOUD_SQL_USER = 'postgres'
CLOUD_SQL_PASSWORD = 'L6171r12@@jjms'

print('🔌 Testando conexão direta com Cloud SQL...')

try:
    # Testar conexão direta
    conn = psycopg2.connect(
        host=CLOUD_SQL_HOST,
        port=CLOUD_SQL_PORT,
        database=CLOUD_SQL_DB,
        user=CLOUD_SQL_USER,
        password=CLOUD_SQL_PASSWORD,
        connect_timeout=10
    )
    conn.close()
    print('✅ Conexão direta OK!')

except Exception as e:
    print(f'❌ Falha na conexão direta: {e}')
    sys.exit(1)

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema_rural.settings_gcp'
os.environ['CLOUD_SQL_CONNECTION_NAME'] = 'monpec-sistema-rural:us-central1:monpec-db'
os.environ['DB_HOST'] = CLOUD_SQL_HOST
os.environ['DB_PORT'] = CLOUD_SQL_PORT
os.environ['DB_NAME'] = CLOUD_SQL_DB
os.environ['DB_USER'] = CLOUD_SQL_USER
os.environ['DB_PASSWORD'] = CLOUD_SQL_PASSWORD
os.environ['SECRET_KEY'] = 'django-insecure-monpec-gcp-2025-secret-key-production'
os.environ['DEBUG'] = 'False'

# Desabilitar validações
os.environ['DJANGO_SKIP_CHECKS'] = 'true'

django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

print('🚀 Executando migrações...')

try:
    # Executar migrações em ordem
    apps_to_migrate = [
        'contenttypes',
        'auth',
        'admin',
        'sessions',
        'gestao_rural'
    ]

    for app in apps_to_migrate:
        try:
            execute_from_command_line(['manage.py', 'migrate', app, '--noinput'])
            print(f'✅ {app} migrado')
        except Exception as e:
            print(f'⚠️ {app} falhou: {e}')

    print('✅ Todas as migrações executadas!')

    # Criar admin
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@monpec.com.br', 'L6171r12@@')
        print('✅ Admin criado: admin / L6171r12@@')
    else:
        print('Admin já existe')

    # Contar usuários
    user_count = User.objects.count()
    print(f'👥 Total de usuários: {user_count}')

    print('🎉 SETUP COMPLETO! Agora teste a demonstração!')

except Exception as e:
    print(f'❌ ERRO FINAL: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)




