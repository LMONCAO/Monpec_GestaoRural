#!/bin/bash
# Executar verificação e continuar com os próximos passos

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "▶ Verificando se tabela foi criada..."
gcloud run jobs execute verify-table-created --region us-central1 --wait

echo ""
echo "▶ Executando todas as migrações restantes..."

# Executar todas as migrações restantes
gcloud run jobs create run-all-remaining-migrations \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,migrate,--noinput \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 900 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

gcloud run jobs execute run-all-remaining-migrations --region us-central1 --wait
gcloud run jobs delete run-all-remaining-migrations --region us-central1 --quiet 2>&1 || true
gcloud run jobs delete verify-table-created --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ Criando admin..."

gcloud run jobs create create-admin-final \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args criar_admin_producao.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

gcloud run jobs execute create-admin-final --region us-central1 --wait
gcloud run jobs delete create-admin-final --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅✅✅ TUDO CONCLUÍDO! ✅✅✅"
echo ""
echo "🔐 CREDENCIAIS:"
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








