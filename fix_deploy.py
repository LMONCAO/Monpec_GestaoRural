#!/usr/bin/env python3
"""
Script para corrigir problemas de deploy no Google Cloud Run
- Corrige permissões do banco
- Executa migrações
- Popula dados iniciais
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

# Configurar variáveis de ambiente
os.environ['DB_NAME'] = 'monpec_db'
os.environ['DB_USER'] = 'monpec_user'
os.environ['DB_PASSWORD'] = 'L6171r12@@jjms'
os.environ['DB_HOST'] = '34.9.51.178'
os.environ['DB_PORT'] = '5432'
os.environ['CLOUD_SQL_CONNECTION_NAME'] = 'monpec-sistema-rural:us-central1:monpec-db'
os.environ['SECRET_KEY'] = 'django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE'

from django.db import connection
from django.core.management import execute_from_command_line
from django.contrib.auth import get_user_model

def fix_database_permissions():
    """Corrige permissões do banco de dados"""
    print("🔧 Corrigindo permissões do banco...")

    cursor = connection.cursor()

    # Conceder permissões na tabela django_session
    try:
        cursor.execute("GRANT ALL PRIVILEGES ON TABLE django_session TO monpec_user;")
        print("✅ Permissões concedidas na tabela django_session")
    except Exception as e:
        print(f"⚠️ Erro ao conceder permissões: {e}")

    # Conceder permissões em todas as tabelas gestao_rural
    try:
        cursor.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO monpec_user;")
        cursor.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO monpec_user;")
        print("✅ Permissões concedidas em todas as tabelas")
    except Exception as e:
        print(f"⚠️ Erro ao conceder permissões gerais: {e}")

    connection.commit()

def run_migrations():
    """Executa migrações pendentes"""
    print("📋 Executando migrações...")

    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrações executadas com sucesso")
    except Exception as e:
        print(f"❌ Erro nas migrações: {e}")

def create_admin_user():
    """Cria usuário administrador"""
    print("👨‍💼 Criando usuário admin...")

    User = get_user_model()
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@monpec.com.br', 'L6171r12@@')
            print("✅ Usuário admin criado")
        else:
            print("✅ Usuário admin já existe")
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")

def populate_initial_data():
    """Popula dados iniciais"""
    print("📊 Populando dados iniciais...")

    try:
        # Importar e executar script de população
        sys.path.append('.')
        from popular_dados_producao import criar_dados_producao_seguros
        criar_dados_producao_seguros()
        print("✅ Dados populados com sucesso")
    except Exception as e:
        print(f"⚠️ Erro ao popular dados: {e}")

if __name__ == '__main__':
    print("🚀 Iniciando correção do deploy...")

    fix_database_permissions()
    run_migrations()
    create_admin_user()
    populate_initial_data()

    print("✅ Correção concluída!")