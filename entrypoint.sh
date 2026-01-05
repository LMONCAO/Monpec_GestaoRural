#!/bin/bash
set -e

# Configurar variável de ambiente PORT se não estiver definida
export PORT=${PORT:-8080}

echo "🚀 Iniciando container..."

# Executar collectstatic se necessário
# Isso garante que os arquivos estáticos estejam sempre atualizados
echo "📦 Coletando arquivos estáticos..."
# Detectar qual settings usar (Fly.io ou GCP)
if [ -n "$FLY_APP_NAME" ]; then
    SETTINGS_MODULE="sistema_rural.settings_flyio"
    echo "🚀 Detectado Fly.io - usando settings_flyio"
else
    SETTINGS_MODULE="sistema_rural.settings_gcp"
    echo "☁️ Detectado Google Cloud - usando settings_gcp"
fi

# Usar DJANGO_SETTINGS_MODULE se definido, senão usar o detectado
if [ -n "$DJANGO_SETTINGS_MODULE" ]; then
    SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE"
    echo "📝 Usando DJANGO_SETTINGS_MODULE: $SETTINGS_MODULE"
fi

# Executar collectstatic se necessário
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings="$SETTINGS_MODULE" || {
    echo "⚠️ collectstatic falhou, mas continuando..."
}

# Executar migrações
echo "🔄 Executando migrações..."
python manage.py migrate --noinput --settings="$SETTINGS_MODULE" || {
    echo "⚠️ Migrações falharam, mas continuando..."
}

# Iniciar o servidor Gunicorn
echo "✅ Iniciando servidor Gunicorn..."
# Reduzir workers para 2 para debug - aumentar timeout e adicionar preload
exec gunicorn sistema_rural.wsgi:application --bind 0.0.0.0:8080 --workers 2 --threads 2 --timeout 600 --access-logfile - --error-logfile - --log-level info
