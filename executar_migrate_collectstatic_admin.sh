#!/bin/bash
# Script para executar migrate, collectstatic e criar admin
# Copie este arquivo para o Cloud Shell e execute: bash executar_migrate_collectstatic_admin.sh

# Criar arquivo de configuração do Cloud Build
cat > /tmp/cloudbuild-migrate.yaml <<'YAML'
steps:
- name: 'gcr.io/monpec-sistema-rural/sistema-rural:latest'
  entrypoint: 'sh'
  args:
  - '-c'
  - |
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')"
  env:
  - 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'
  - 'DB_NAME=monpec_db'
  - 'DB_USER=monpec_user'
  - 'DB_PASSWORD=L6171r12@@jjms'
  - 'CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db'
YAML

# Executar o build
echo "Executando migrate, collectstatic e criação do admin..."
gcloud builds submit --config=/tmp/cloudbuild-migrate.yaml .

# Limpar arquivo temporário
rm -f /tmp/cloudbuild-migrate.yaml

echo "✅ Concluído!"

