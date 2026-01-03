#!/bin/bash
# Solução robusta: verificar estado e executar migrações uma por uma se necessário

set +H  # Desabilita history expansion
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "🔍 Verificando estado das migrações..."

# Verificar quais migrações já foram aplicadas
gcloud run jobs create check-state \
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
OUTPUT=$(gcloud run jobs execute check-state --region us-central1 --wait 2>&1 | tail -100)
echo "$OUTPUT"
gcloud run jobs delete check-state --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ Executando todas as migrações (o Django vai pular as que já foram aplicadas)..."

# Executar migrações normalmente - Django vai pular as que já foram aplicadas
gcloud run jobs create run-all-migrations \
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

echo "Executando migrações (pode levar alguns minutos)..."
MIGRATION_OUTPUT=$(gcloud run jobs execute run-all-migrations --region us-central1 --wait 2>&1)
echo "$MIGRATION_OUTPUT" | tail -100

# Verificar se houve erro
if echo "$MIGRATION_OUTPUT" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Erro nas migrações. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=run-all-migrations AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -100
    gcloud run jobs delete run-all-migrations --region us-central1 --quiet 2>&1 || true
    exit 1
fi

gcloud run jobs delete run-all-migrations --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Migrações concluídas!"
echo ""
echo "▶ Criando admin..."

# Criar admin usando arquivo Python temporário (mais robusto)
gcloud run jobs create create-admin-robust \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args /app/criar_admin_producao.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

# Se o arquivo não existir, usar comando inline
if [ $? -ne 0 ] || ! gcloud run jobs execute create-admin-robust --region us-central1 --wait 2>&1 | tail -20; then
    echo "Tentando método alternativo (comando inline)..."
    gcloud run jobs delete create-admin-robust --region us-central1 --quiet 2>&1 || true
    
    gcloud run jobs create create-admin-inline \
      --image gcr.io/$PROJECT_ID/monpec \
      --region us-central1 \
      --command python \
      --args -c,"import os;os.environ['DJANGO_SETTINGS_MODULE']='sistema_rural.settings_gcp';import django;django.setup();from django.contrib.auth import get_user_model;User=get_user_model();u,created=User.objects.get_or_create(username='admin',defaults={'email':'admin@monpec.com.br','is_superuser':True,'is_staff':True,'is_active':True});u.set_password('L6171r12@@');u.is_superuser=True;u.is_staff=True;u.is_active=True;u.save();print('SUCCESS: Admin criado')" \
      --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
      --set-cloudsql-instances $CONNECTION_NAME \
      --max-retries 1 \
      --task-timeout 300 \
      --memory 512Mi \
      --cpu 1 2>&1 | grep -v "already exists" || true
    
    ADMIN_OUTPUT=$(gcloud run jobs execute create-admin-inline --region us-central1 --wait 2>&1)
    echo "$ADMIN_OUTPUT" | tail -30
    gcloud run jobs delete create-admin-inline --region us-central1 --quiet 2>&1 || true
else
    gcloud run jobs delete create-admin-robust --region us-central1 --quiet 2>&1 || true
fi

echo ""
echo "✅ CONCLUÍDO!"
echo ""
echo "🔐 Credenciais:"
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








