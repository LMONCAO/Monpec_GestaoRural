#!/bin/bash

# Entrypoint SIMPLIFICADO para Cloud Run - focado em iniciar rápido
export PORT=${PORT:-8080}

echo "🚀 Iniciando MONPEC - versão Cloud Run..."

SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp_deploy}"
echo "Settings: $SETTINGS_MODULE"

# 1. Aplicar migrações essenciais (só o básico para iniciar)
echo "📋 Aplicando migrações essenciais..."
python manage.py migrate --run-syncdb --settings="$SETTINGS_MODULE" || {
    echo "⚠️ Migrações falharam, tentando fake para conflitos..."
    python manage.py migrate gestao_rural --fake --settings="$SETTINGS_MODULE" 2>/dev/null || echo "⚠️ Fake falhou"
    python manage.py migrate --settings="$SETTINGS_MODULE" || echo "❌ Migrações críticas falharam"
}

# 2. Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings="$SETTINGS_MODULE" || echo "⚠️ Collectstatic falhou"

# 3. Criar administrador básico
echo "👨‍💼 Criando administrador..."
python manage.py shell --settings="$SETTINGS_MODULE" -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com.br', 'admin123')
    print('Admin criado')
else:
    print('Admin já existe')
" 2>/dev/null || echo "⚠️ Admin creation failed"

# 4. Iniciar servidor Gunicorn (simplificado para iniciar rápido)
echo "✅ Iniciando servidor Gunicorn..."
exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
