#!/usr/bin/env python
"""
SCRIPT PARA RESETAR BANCO COMPLETAMENTE
"""

import os
import django
from django.conf import settings
from django.db import connection

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
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
    SECRET_KEY='django-insecure-reset',
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'gestao_rural',
    ]
)

django.setup()

def reset_database():
    """Reseta completamente o banco de dados"""
    with connection.cursor() as cursor:
        print("🗑️ REMOVENDO TODAS AS TABELAS DJANGO...")

        # Desabilitar foreign key checks
        cursor.execute("SET session_replication_role = 'replica';")

        # Dropar todas as tabelas Django
        cursor.execute("""
            DROP TABLE IF EXISTS
                gestao_rural_fluxocaixa,
                gestao_rural_custovariavel,
                gestao_rural_movimentacaoprojetada,
                gestao_rural_categoriacusto,
                gestao_rural_categoriaanimal,
                gestao_rural_cenario,
                gestao_rural_planejamento,
                gestao_rural_folhapagamento,
                gestao_rural_funcionario,
                gestao_rural_equipamento,
                gestao_rural_tipoequipamento,
                gestao_rural_estoquesuplementacao,
                gestao_rural_animalindividual,
                gestao_rural_brincoanimal,
                gestao_rural_manejo,
                gestao_rural_pastagem,
                gestao_rural_modulo,
                gestao_rural_propriedade,
                gestao_rural_produtor,
                gestao_rural_logauditoria,
                django_migrations,
                django_session,
                django_admin_log,
                django_content_type,
                auth_permission,
                auth_group_permissions,
                auth_group,
                auth_user_groups,
                auth_user_user_permissions,
                auth_user
            CASCADE;
        """)

        # Reabilitar foreign key checks
        cursor.execute("SET session_replication_role = 'origin';")

        print("✅ TABELAS REMOVIDAS")
        print("🔄 BANCO RESETADO COMPLETAMENTE")

if __name__ == '__main__':
    try:
        reset_database()
        print("🎉 RESET CONCLUÍDO!")
    except Exception as e:
        print(f"❌ ERRO NO RESET: {e}")
        import traceback
        traceback.print_exc()