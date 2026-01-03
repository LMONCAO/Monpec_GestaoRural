import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_producao')

# Get the WSGI application
application = get_wsgi_application()
