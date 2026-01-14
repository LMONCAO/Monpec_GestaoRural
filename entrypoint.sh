#!/bin/bash

# Entrypoint ULTRA SIMPLIFICADO para Cloud Run
export PORT=${PORT:-8080}

echo "🚀 Iniciando MONPEC Cloud Run..."

# Configurações mínimas
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp_deploy}"

# Migrações essenciais apenas
echo "📋 Aplicando migrações..."
python manage.py migrate --run-syncdb --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null || echo "⚠️ Migrações básicas falharam"

# Iniciar servidor imediatamente
echo "✅ Iniciando Gunicorn..."
exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 1 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level warning
