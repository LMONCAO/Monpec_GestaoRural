#!/usr/bin/env python
"""
SCRIPT DE DIAGNÓSTICO DO BANCO DE DADOS
Execute este script localmente para identificar problemas
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection
from django.core.management import execute_from_command_line

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')

# Configurações do banco (ajuste conforme necessário)
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'monpec-db',
            'USER': 'postgres',
            'PASSWORD': 'L6171r12@@jjms',
            'HOST': '34.9.51.178',
            'PORT': '5432',
        }
    },
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'gestao_rural',
        'sistema_rural',
    ],
    SECRET_KEY='django-insecure-diagnostico-local',
)

django.setup()

def testar_conexao():
    """Testa conexão com o banco"""
    print("🔍 TESTANDO CONEXÃO COM BANCO...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Conexão OK: {version[0][:50]}...")
        return True
    except Exception as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        return False

def verificar_tabelas():
    """Verifica tabelas existentes"""
    print("\n🔍 VERIFICANDO TABELAS EXISTENTES...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            django_tables = [t[0] for t in tables if t[0].startswith('gestao_rural_')]
            print(f"📊 Tabelas Django encontradas: {len(django_tables)}")
            for table in django_tables[:10]:  # Mostra primeiras 10
                print(f"  - {table}")
            if len(django_tables) > 10:
                print(f"  ... e mais {len(django_tables) - 10} tabelas")
        return django_tables
    except Exception as e:
        print(f"❌ ERRO ao verificar tabelas: {e}")
        return []

def verificar_migracoes():
    """Verifica status das migrações"""
    print("\n🔍 VERIFICANDO STATUS DAS MIGRAÇÕES...")
    try:
        from django.db.migrations.recorder import MigrationRecorder
        from django.db.migrations.loader import MigrationLoader

        loader = MigrationLoader(connection, ignore_no_migrations=True)
        recorder = MigrationRecorder(connection)

        applied = recorder.applied_migrations()
        print(f"📋 Migrações aplicadas: {len(applied)}")

        # Verificar migrações pendentes
        pending = []
        for app_label, migrations in loader.disk_migrations.items():
            for migration in migrations:
                if (app_label, migration.name) not in applied:
                    pending.append(f"{app_label}.{migration.name}")

        if pending:
            print(f"⏳ Migrações pendentes: {len(pending)}")
            for mig in pending[:5]:  # Mostra primeiras 5
                print(f"  - {mig}")
        else:
            print("✅ Todas as migrações estão aplicadas")

        return applied, pending
    except Exception as e:
        print(f"❌ ERRO ao verificar migrações: {e}")
        return [], []

def verificar_propriedades():
    """Verifica propriedades existentes"""
    print("\n🔍 VERIFICANDO PROPRIEDADES...")
    try:
        from gestao_rural.models import Propriedade
        count = Propriedade.objects.count()
        print(f"🏠 Propriedades encontradas: {count}")

        if count > 0:
            props = Propriedade.objects.all()[:5]
            for prop in props:
                print(f"  - ID {prop.id}: {prop.nome} (Produtor: {prop.produtor})")

        return count
    except Exception as e:
        print(f"❌ ERRO ao verificar propriedades: {e}")
        return 0

def testar_migrate():
    """Testa comando migrate"""
    print("\n🔍 TESTANDO COMANDO MIGRATE...")
    try:
        from django.core.management import call_command
        print("⏳ Executando migrate --dry-run...")
        call_command('migrate', dry_run=True, verbosity=1)
        print("✅ Migrate dry-run OK")
        return True
    except Exception as e:
        print(f"❌ ERRO no migrate dry-run: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 DIAGNÓSTICO COMPLETO DO BANCO MONPEC")
    print("=" * 60)

    # Testes
    conexao_ok = testar_conexao()
    if not conexao_ok:
        print("\n❌ IMPOSSÍVEL CONTINUAR - SEM CONEXÃO COM BANCO")
        return

    tabelas = verificar_tabelas()
    applied, pending = verificar_migracoes()
    propriedades = verificar_propriedades()
    migrate_ok = testar_migrate()

    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO:")
    print("=" * 60)
    print(f"🔗 Conexão: {'✅ OK' if conexao_ok else '❌ FALHA'}")
    print(f"📊 Tabelas Django: {len(tabelas)}")
    print(f"📋 Migrações aplicadas: {len(applied)}")
    print(f"⏳ Migrações pendentes: {len(pending)}")
    print(f"🏠 Propriedades: {propriedades}")
    print(f"🔄 Migrate test: {'✅ OK' if migrate_ok else '❌ FALHA'}")

    if pending:
        print("
⚠️  RECOMENDAÇÃO: Execute migrate para aplicar migrações pendentes"    else:
        print("
✅ SISTEMA PRONTO: Todas as migrações aplicadas"    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()