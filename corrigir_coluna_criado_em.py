#!/usr/bin/env python
"""
Script para corrigir a coluna criado_em faltante na tabela gestao_rural_lancamentofinanceiro
"""

import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

# Tentar configurar com as configurações do GCP se disponível
try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    print("Tentando com configurações alternativas...")

    # Configuração manual se necessário
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'monpec-db',  # Ajuste conforme necessário
                'USER': 'postgres',
                'PASSWORD': 'L6171r12@@jjms',  # Ajuste conforme necessário
                'HOST': '34.9.51.178',  # Ajuste conforme necessário
                'PORT': '5432',
            }
        },
        SECRET_KEY='django-insecure-corrigir-coluna',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'gestao_rural',
        ]
    )
    django.setup()

from django.db import connection

def corrigir_coluna_criado_em():
    """Adiciona a coluna criado_em à tabela se ela não existir"""
    with connection.cursor() as cursor:
        try:
            print("🔍 Verificando se a coluna criado_em existe...")

            # Verificar se a coluna existe
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'gestao_rural_lancamentofinanceiro'
                AND column_name = 'criado_em';
            """)

            coluna_existe = cursor.fetchone()

            if coluna_existe:
                print("✅ A coluna criado_em já existe na tabela!")
                return True

            print("❌ Coluna criado_em não encontrada. Adicionando...")

            # Adicionar a coluna
            cursor.execute("""
                ALTER TABLE gestao_rural_lancamentofinanceiro
                ADD COLUMN criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW();
            """)

            # Verificar se foi adicionada com sucesso
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'gestao_rural_lancamentofinanceiro'
                AND column_name = 'criado_em';
            """)

            if cursor.fetchone():
                print("✅ Coluna criado_em adicionada com sucesso!")

                # Preencher valores existentes com NOW()
                cursor.execute("""
                    UPDATE gestao_rural_lancamentofinanceiro
                    SET criado_em = NOW()
                    WHERE criado_em IS NULL;
                """)

                print("✅ Valores preenchidos para registros existentes!")
                return True
            else:
                print("❌ Erro: Coluna não foi criada!")
                return False

        except Exception as e:
            print(f"❌ Erro ao corrigir coluna: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("🚀 Iniciando correção da coluna criado_em...")
    sucesso = corrigir_coluna_criado_em()

    if sucesso:
        print("\n🎉 Correção concluída! O erro deve estar resolvido.")
        print("Você pode testar acessando as funcionalidades que estavam falhando.")
    else:
        print("\n❌ Falha na correção. Verifique os logs de erro acima.")