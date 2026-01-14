#!/bin/bash

# LOG INICIAL PARA CONFIRMAR EXECUÇÃO
echo "=========================================="
echo "🚀 ENTRYPOINT.SH INICIADO!"
echo "=========================================="
date
whoami
pwd
ls -la /app/
echo "=========================================="

# Entrypoint MONPEC - versão de debug para resolver Service Unavailable
export PORT=${PORT:-8080}

echo "🚀 MONPEC Cloud Run - DEBUG MODE"
echo "📍 Porta: $PORT"
echo "📊 DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

# Configuração
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp_deploy}"

# Testes detalhados
echo "🐍 Testando Python..."
python3 --version

echo "📦 Testando Django..."
python3 -c "import django; print('Django version:', django.get_version())"

echo "⚙️ Testando settings..."
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
import django
django.setup()
print('✅ Django setup OK')
print('📊 Installed apps:', len(django.apps.apps.get_app_configs()))
"

echo "🗄️ Testando banco de dados..."
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1 as test')
        result = cursor.fetchone()
        print('✅ Banco OK, teste SELECT:', result)
except Exception as e:
    print('❌ ERRO BANCO:', str(e))
    import traceback
    traceback.print_exc()
"

echo "📋 Executando migrações..."
python3 manage.py showmigrations --settings="$DJANGO_SETTINGS_MODULE" | head -10

echo "🚀 Iniciando Gunicorn..."
exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 1 \
    --timeout 60 \
    --log-level debug \
    --access-logfile - \
    --error-logfile -
