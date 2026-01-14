#!/bin/bash

# Entrypoint ULTRA SIMPLIFICADO para Cloud Run com DEBUG
export PORT=${PORT:-8080}

echo "🚀 DEBUG: Iniciando MONPEC Cloud Run..."
echo "🚀 DEBUG: PORT=$PORT"
echo "🚀 DEBUG: PYTHONPATH=$PYTHONPATH"
echo "🚀 DEBUG: DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Verificar se Python está funcionando
echo "🐍 DEBUG: Testando Python..."
python --version || exit 1

# Verificar se Django está instalado
echo "📦 DEBUG: Testando Django..."
python -c "import django; print('Django OK')" || exit 1

# Verificar se gunicorn está instalado
echo "🐴 DEBUG: Testando Gunicorn..."
gunicorn --version || exit 1

# Configurações mínimas
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp_deploy}"
echo "⚙️ DEBUG: DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"

# Migrações essenciais apenas
echo "📋 Aplicando migrações..."
python manage.py migrate --run-syncdb --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null || {
    echo "❌ DEBUG: Migrações falharam"
    python manage.py check --settings="$DJANGO_SETTINGS_MODULE" || echo "❌ DEBUG: Django check failed"
    exit 1
}
echo "✅ DEBUG: Migrações OK"

# Testar se o Django consegue iniciar
echo "🧪 DEBUG: Testando Django app..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
import django
django.setup()
print('✅ DEBUG: Django setup OK')
" || exit 1

# Iniciar servidor
echo "✅ Iniciando Gunicorn na porta $PORT..."
exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 1 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
