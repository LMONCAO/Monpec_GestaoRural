#!/bin/bash
# Script para corrigir problemas de deploy no Cloud Shell

echo "🔧 Corrigindo deploy do MONPEC..."

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Conceder permissões no banco
echo "🔑 Corrigindo permissões do banco..."
gcloud sql instances patch monpec-db --authorized-networks=0.0.0.0/0

# Criar job para executar correções
echo "📋 Criando job de correção..."
gcloud run jobs create monpec-fix \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="bash" \
  --args="-c,python manage.py migrate --noinput && python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@monpec.com.br', 'L6171r12@@')\" && python popular_dados_producao.py"

# Executar job
echo "🚀 Executando correções..."
gcloud run jobs execute monpec-fix --region us-central1 --wait

# Deletar job
gcloud run jobs delete monpec-fix --region us-central1 --quiet

echo "✅ Correções aplicadas! Faça um novo deploy."