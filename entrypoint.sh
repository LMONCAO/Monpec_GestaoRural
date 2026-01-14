#!/bin/bash

# Entrypoint MONPEC - versão ultra simples para funcionar
export PORT=${PORT:-8080}

echo "🚀 MONPEC Cloud Run iniciando..."
echo "📍 Porta: $PORT"

# Configuração mínima
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp_deploy}"

# Apenas verificações críticas
python3 -c "import django; print('✅ Django import OK')" || exit 1

# Migração mínima (só o essencial)
python3 manage.py migrate --run-syncdb --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null && echo "✅ Migrações OK" || echo "⚠️ Migrações falharam"

# Iniciar Gunicorn imediatamente
echo "🚀 Iniciando servidor..."
exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 1 \
    --timeout 60 \
    --log-level warning
