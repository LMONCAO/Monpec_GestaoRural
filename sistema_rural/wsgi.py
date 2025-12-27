"""
WSGI config for sistema_rural project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import platform

from django.core.wsgi import get_wsgi_application

# Detectar ambiente e configurar settings apropriado
# Se DJANGO_SETTINGS_MODULE não estiver definido, detectar automaticamente
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    # Verificar se está no Google Cloud (App Engine ou Cloud Run)
    if os.getenv('GAE_ENV') is not None or os.getenv('K_SERVICE') is not None:
        # Google Cloud Platform - usar settings_gcp
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
    # Verificar se está no servidor Locaweb (Linux e não é Windows)
    elif platform.system() != 'Windows' and os.getenv('LOCAWEB_SERVER', '').lower() == 'true':
        # Servidor Locaweb - usar settings_producao
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_producao')
    # Verificar se o hostname contém monpec.com.br (servidor de produção)
    elif 'monpec.com.br' in os.getenv('HTTP_HOST', '') or 'monpec.com.br' in os.getenv('SERVER_NAME', ''):
        # Servidor de produção - usar settings_producao
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_producao')
    else:
        # Desenvolvimento local - usar settings padrão
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
else:
    # Se já estiver definido, usar o valor existente
    pass

application = get_wsgi_application()

