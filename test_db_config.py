#!/usr/bin/env python
import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema_rural.settings_producao'

import django
django.setup()

from django.conf import settings

print('Database Engine:', settings.DATABASES['default']['ENGINE'])
print('Database Name:', settings.DATABASES['default']['NAME'])
print('Database User:', settings.DATABASES['default'].get('USER', 'N/A'))
print('Database Host:', settings.DATABASES['default'].get('HOST', 'N/A'))
print('Database Port:', settings.DATABASES['default'].get('PORT', 'N/A'))