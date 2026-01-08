#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings

# Configurar Django manualmente
settings.configure(
    DEBUG=False,
    SECRET_KEY='django-insecure-test-key',
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'sistema_rural',
            'USER': 'monpec',
            'PASSWORD': 'L6171r12@@jjms',
            'HOST': 'localhost',
            'PORT': '5432',
            'OPTIONS': {
                'client_encoding': 'UTF8',
            },
        }
    },
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ],
    USE_TZ=True,
)

django.setup()

print('Database Engine:', settings.DATABASES['default']['ENGINE'])
print('Database Name:', settings.DATABASES['default']['NAME'])
print('Database User:', settings.DATABASES['default']['USER'])
print('Database Host:', settings.DATABASES['default']['HOST'])
print('Database Port:', settings.DATABASES['default']['PORT'])

# Testar conexão
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print('PostgreSQL connection successful!')
    print('Version:', version[0][:50] + '...')
except Exception as e:
    print('PostgreSQL connection failed:', str(e))