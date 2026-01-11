#!/usr/bin/env python
"""
TESTE DE CONEXÃO DIRETO NO CLOUD RUN
Execute este script no Cloud Shell para testar
"""

import os
import sys
import django
from django.conf import settings

# Configurar ambiente
os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema_rural.settings_gcp'
os.environ['DB_HOST'] = '34.9.51.178'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'monpec-db'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'L6171r12@@jjms'
os.environ['SECRET_KEY'] = 'django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE'

try:
    django.setup()
    print("✅ Django setup OK")
except Exception as e:
    print(f"❌ Django setup ERROR: {e}")
    sys.exit(1)

try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Database connection OK: {result}")
except Exception as e:
    print(f"❌ Database connection ERROR: {e}")
    sys.exit(1)

try:
    from gestao_rural.models import Propriedade
    count = Propriedade.objects.count()
    print(f"✅ Models OK - Propriedades: {count}")
except Exception as e:
    print(f"❌ Models ERROR: {e}")
    sys.exit(1)

print("🎉 ALL TESTS PASSED!")