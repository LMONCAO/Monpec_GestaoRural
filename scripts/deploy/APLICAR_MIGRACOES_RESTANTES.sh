#!/bin/bash
# Aplicar migrações restantes após 0071

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "▶ Verificando quais migrações ainda faltam..."

# Verificar estado das migrações
gcloud run jobs create check-remaining-migrations \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,showmigrations,gestao_rural \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo "Executando verificação..."
CHECK_OUTPUT=$(gcloud run jobs execute check-remaining-migrations --region us-central1 --wait 2>&1)
echo "$CHECK_OUTPUT" | grep -A 50 "gestao_rural" || echo "$CHECK_OUTPUT" | tail -100
gcloud run jobs delete check-remaining-migrations --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ Aplicando migrações restantes (a partir de 0072)..."

# Aplicar especificamente a partir de 0072
gcloud run jobs create apply-from-72 \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,migrate,gestao_rural,0072_adicionar_campos_obrigatorios_nfe_produto \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo "Executando migração 0072..."
MIG72_OUTPUT=$(gcloud run jobs execute apply-from-72 --region us-central1 --wait 2>&1)
echo "$MIG72_OUTPUT" | tail -100
gcloud run jobs delete apply-from-72 --region us-central1 --quiet 2>&1 || true

if echo "$MIG72_OUTPUT" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Erro na migração 0072. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=apply-from-72 AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -100
    exit 1
fi

echo ""
echo "▶ Executando todas as migrações restantes..."

# Executar todas as migrações restantes
gcloud run jobs create run-all-remaining-final \
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

MIG_ALL_OUTPUT=$(gcloud run jobs execute run-all-remaining-final --region us-central1 --wait 2>&1)
echo "$MIG_ALL_OUTPUT" | tail -100
gcloud run jobs delete run-all-remaining-final --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Migrações concluídas!"
echo ""
echo "🔐 O admin já foi criado anteriormente."
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








