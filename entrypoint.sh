#!/bin/bash

# VERSÃO FINAL: Django com Cloud SQL
export PORT=${PORT:-8080}

echo "🚀 MONPEC Cloud Run - VERSÃO FINAL"
echo "📍 Porta: $PORT"
echo "⏰ Hora: $(date)"

# Configurações Django
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp_deploy}"

# Verificações básicas
echo "🐍 Verificando Python..."
python3 -c "print('✅ Python OK')" || exit 1

echo "📦 Verificando Django..."
python3 -c "import django; print('✅ Django OK')" || exit 1

echo "🐴 Verificando Gunicorn..."
python3 -c "import gunicorn; print('✅ Gunicorn OK')" || exit 1

# Aguardar Cloud SQL ficar disponível (máximo 60 segundos)
echo "⏳ Aguardando Cloud SQL..."
for i in {1..60}; do
    if python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
import django
from django.conf import settings
django.setup()

from django.db import connections
from django.db.utils import OperationalError

try:
    conn = connections['default']
    conn.ensure_connection()
    print('✅ Banco OK')
    exit(0)
except OperationalError as e:
    print(f'⏳ Aguardando banco... {e}')
    exit(1)
"; then
        echo "✅ Cloud SQL conectado!"
        break
    fi

    if [ $i -eq 60 ]; then
        echo "❌ Timeout: Cloud SQL não disponível após 60 segundos"
        echo "📋 Verificando variáveis de ambiente..."
        env | grep -E "(DATABASE|DB_|DJANGO)" || echo "⚠️ Nenhuma variável DB encontrada"
        exit 1
    fi

    echo "⏳ Tentativa $i/60 - Aguardando 2 segundos..."
    sleep 2
done

# Aplicar migrações
echo "📋 Aplicando migrações..."
python3 manage.py migrate --run-syncdb --settings="$DJANGO_SETTINGS_MODULE" || {
    echo "⚠️ Migrações falharam, tentando continuar..."
}

# Coletar estáticos (opcional)
echo "📦 Coletando estáticos..."
python3 manage.py collectstatic --noinput --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null || echo "⚠️ Collectstatic falhou"

# Criar admin (opcional)
echo "👨‍💼 Verificando admin..."
python3 manage.py shell --settings="$DJANGO_SETTINGS_MODULE" -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com.br', 'admin123')
    print('✅ Admin criado')
else:
    print('✅ Admin existe')
" 2>/dev/null || echo "⚠️ Admin falhou"

# Iniciar Django
echo "🚀 Iniciando Django na porta $PORT..."
exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
