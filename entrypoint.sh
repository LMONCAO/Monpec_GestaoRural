#!/bin/bash
set -e

echo "🚀 Iniciando container..."

# Executar collectstatic se necessário
# Isso garante que os arquivos estáticos estejam sempre atualizados
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=sistema_rural.settings_gcp || {
    echo "⚠️ collectstatic falhou, mas continuando..."
}

# Executar migrações (opcional - pode ser feito manualmente ou via Cloud Run Jobs)
# echo "🔄 Executando migrações..."
# python manage.py migrate --noinput --settings=sistema_rural.settings_gcp || {
#     echo "⚠️ Migrações falharam, mas continuando..."
# }

# Iniciar o servidor Gunicorn
echo "✅ Iniciando servidor Gunicorn..."
exec gunicorn sistema_rural.wsgi:application --bind 0.0.0.0:8080 --workers 4 --threads 2 --timeout 600
