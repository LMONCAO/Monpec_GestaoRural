@echo off
cd /d "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"
python -c "
import os
print('Current directory:', os.getcwd())
os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema_rural.settings_producao'
import django
django.setup()
from django.conf import settings
print('Database Engine:', settings.DATABASES['default']['ENGINE'])
print('Database Name:', settings.DATABASES['default']['NAME'])
print('Database User:', settings.DATABASES['default']['USER'])
print('Database Host:', settings.DATABASES['default']['HOST'])
print('Database Port:', settings.DATABASES['default']['PORT'])
"
pause