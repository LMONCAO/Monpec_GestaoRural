#!/bin/bash

# Entrypoint MONPEC - versão final funcionando
export PORT=${PORT:-8080}

echo "🚀 Iniciando MONPEC Cloud Run..."
echo "📍 Porta: $PORT"

# Configurações Django
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp_deploy}"

# Verificações rápidas
echo "🐍 Verificando Python..."
python3 -c "print('✅ Python OK')" || exit 1

echo "📦 Verificando Django..."
python3 -c "import django; print('✅ Django OK')" || exit 1

echo "🐴 Verificando Gunicorn..."
python3 -c "import gunicorn; print('✅ Gunicorn OK')" || exit 1

# Migrações essenciais
echo "📋 Aplicando migrações..."
python3 manage.py migrate --run-syncdb --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null || echo "⚠️ Migrações básicas falharam"

# Coletar estáticos
echo "📦 Coletando estáticos..."
python3 manage.py collectstatic --noinput --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null || echo "⚠️ Collectstatic falhou"

# Iniciar Django com Gunicorn
echo "✅ Iniciando Django na porta $PORT..."
exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
