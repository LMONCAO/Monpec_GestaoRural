#!/bin/sh
set -e

echo "🚀 Iniciando aplicação MONPEC..."

# Executar migrações
echo "📦 Executando migrações do banco de dados..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput || echo "⚠️ Aviso: Erro ao coletar arquivos estáticos (pode ser normal se não houver arquivos estáticos)"

# Criar superusuário se não existir
echo "👤 Verificando superusuário..."
if [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py garantir_admin --senha "${DJANGO_SUPERUSER_PASSWORD}" || echo "⚠️ Aviso: Não foi possível garantir admin"
else
  echo "⚠️ Aviso: DJANGO_SUPERUSER_PASSWORD não definido; pulando criação/garantia de admin"
fi

# Iniciar servidor
echo "🌐 Iniciando servidor Gunicorn..."
PORT=${PORT:-8080}
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - sistema_rural.wsgi:application

