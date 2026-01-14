#!/usr/bin/env python
"""
SCRIPT PARA CORREÇÃO DE MIGRAÇÕES NO GOOGLE CLOUD
Resolve problemas de tabelas faltantes e erro 500
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp_deploy')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.apps import apps

def main():
    print("🔧 CORREÇÃO DE MIGRAÇÕES GCP - MONPEC")
    print("=" * 50)

    # 1. Verificar conexão com banco
    print("\n1. 🗄️ TESTANDO CONEXÃO COM BANCO...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexão com PostgreSQL OK")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

    # 2. Criar banco se não existir
    print("\n2. 🏗️ CRIANDO BANCO SE NECESSÁRIO...")
    db_name = connection.settings_dict.get('NAME', 'monpec-db')
    try:
        # Conectar ao banco postgres para criar o banco se necessário
        from django.db import connections
        admin_conn = connections['default'].copy()
        admin_conn.settings_dict['NAME'] = 'postgres'

        with admin_conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", [db_name])
            if not cursor.fetchone():
                print(f"📝 Criando banco: {db_name}")
                cursor.execute(f"CREATE DATABASE {db_name}")
                print("✅ Banco criado com sucesso")
            else:
                print("✅ Banco já existe")
    except Exception as e:
        print(f"⚠️ Aviso ao criar banco: {e} (pode ser normal se já existir)")

    # 3. Executar migrações
    print("\n3. 🔄 EXECUTANDO MIGRAÇÕES...")
    try:
        print("Executando: python manage.py migrate --run-syncdb")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        print("✅ Migrações executadas com sucesso")
    except Exception as e:
        print(f"❌ Erro nas migrações: {e}")
        return False

    # 4. Criar tabelas faltantes manualmente se necessário
    print("\n4. 📋 VERIFICANDO/CRIANDO TABELAS FALTANTES...")

    tables_to_create = [
        # Tabelas que podem estar faltando
        ('gestao_rural_assinaturacliente', '''
            CREATE TABLE IF NOT EXISTS gestao_rural_assinaturacliente (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES auth_user(id),
                plano_id INTEGER REFERENCES gestao_rural_planassinatura(id),
                status VARCHAR(20) DEFAULT 'PENDENTE',
                gateway_pagamento VARCHAR(50) DEFAULT 'mercadopago',
                ultimo_checkout_id VARCHAR(255),
                current_period_end TIMESTAMP,
                metadata JSONB DEFAULT '{}',
                data_liberacao DATE,
                cancelamento_agendado BOOLEAN DEFAULT FALSE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mercadopago_customer_id VARCHAR(255),
                mercadopago_subscription_id VARCHAR(255),
                produtor_id INTEGER REFERENCES gestao_rural_produtor(id)
            )
        '''),
        ('gestao_rural_usuarioativo', '''
            CREATE TABLE IF NOT EXISTS gestao_rural_usuarioativo (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES auth_user(id),
                nome_completo VARCHAR(255),
                email VARCHAR(255),
                telefone VARCHAR(20),
                ativo BOOLEAN DEFAULT TRUE,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''),
        ('gestao_rural_tenantworkspace', '''
            CREATE TABLE IF NOT EXISTS gestao_rural_tenantworkspace (
                id SERIAL PRIMARY KEY,
                assinatura_id INTEGER REFERENCES gestao_rural_assinaturacliente(id),
                alias VARCHAR(100) UNIQUE,
                caminho_banco VARCHAR(255),
                status VARCHAR(20) DEFAULT 'ATIVO',
                provisionado_em TIMESTAMP,
                ultimo_erro TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''),
    ]

    created_tables = 0
    for table_name, create_sql in tables_to_create:
        try:
            with connection.cursor() as cursor:
                cursor.execute(create_sql)
            print(f"✅ Tabela criada/verificada: {table_name}")
            created_tables += 1
        except Exception as e:
            print(f"⚠️ Erro ao criar {table_name}: {e}")

    print(f"📊 Tabelas processadas: {created_tables}")

    # 5. Verificar tabelas críticas
    print("\n5. 🔍 VERIFICANDO TABELAS CRÍTICAS...")
    critical_tables = [
        'auth_user',
        'gestao_rural_produtor',
        'gestao_rural_planassinatura',
        'gestao_rural_assinaturacliente',
        'gestao_rural_usuarioativo',
        'gestao_rural_propriedade',
    ]

    existing_tables = 0
    for table in critical_tables:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM information_schema.tables WHERE table_name = %s", [table])
                if cursor.fetchone():
                    print(f"✅ {table}")
                    existing_tables += 1
                else:
                    print(f"❌ {table} - FALTANDO")
        except Exception as e:
            print(f"⚠️ Erro ao verificar {table}: {e}")

    print(f"📊 Tabelas críticas encontradas: {existing_tables}/{len(critical_tables)}")

    # 6. Criar dados básicos se necessário
    print("\n6. 🌱 CRIANDO DADOS BÁSICOS...")
    try:
        # Criar planos básicos se não existirem
        from gestao_rural.models import PlanoAssinatura
        if PlanoAssinatura.objects.count() == 0:
            PlanoAssinatura.objects.create(
                nome='Plano Básico',
                slug='basico',
                descricao='Plano básico para produtores',
                preco_mensal_referencia=69.90,
                max_usuarios=1,
                modulos_disponiveis=['dashboard_pecuaria', 'curral', 'cadastro'],
                recursos='{"pecuaria": true, "financeiro": true}',
                ativo=True,
                popular=False,
                recomendado=False,
                ordem_exibicao=1
            )
            print("✅ Plano Básico criado")

        # Criar superusuário se não existir
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@monpec.com.br',
                password='admin123',
                first_name='Administrador',
                last_name='MONPEC'
            )
            print("✅ Superusuário criado (admin/admin123)")

    except Exception as e:
        print(f"⚠️ Erro ao criar dados básicos: {e}")

    # 7. Teste final
    print("\n7. 🧪 TESTE FINAL DO SISTEMA...")
    try:
        # Testar se conseguimos fazer uma query básica
        from django.contrib.auth.models import User
        user_count = User.objects.count()
        print(f"✅ Query básica funcionando: {user_count} usuários")

        # Testar importações críticas
        try:
            from gestao_rural.services.payments.factory import PaymentGatewayFactory
            print("✅ Payment Gateway OK")
        except Exception as e:
            print(f"⚠️ Payment Gateway: {e}")

        try:
            from gestao_rural.services.notificacoes import enviar_email_customizado
            print("✅ Sistema de email OK")
        except Exception as e:
            print(f"⚠️ Sistema de email: {e}")

        print("🎉 SISTEMA PRONTO PARA GCP!")

    except Exception as e:
        print(f"❌ Erro no teste final: {e}")
        return False

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)