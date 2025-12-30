#!/bin/bash
# Executar o job de migrações que já foi criado

echo "▶ Executando job run-migrations-normal..."
gcloud run jobs execute run-migrations-normal --region us-central1 --wait

echo ""
echo "✅ Migrações executadas!"
echo ""
echo "▶ Agora criando o admin..."

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

gcloud run jobs create create-admin-final \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os,django,sys;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();u,created=User.objects.get_or_create(username='admin',defaults={'email':'admin@monpec.com.br','is_superuser':True,'is_staff':True,'is_active':True});u.set_password('L6171r12@@');u.is_superuser=True;u.is_staff=True;u.is_active=True;u.save();print('✅ Admin criado/atualizado com sucesso!')" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

gcloud run jobs execute create-admin-final --region us-central1 --wait 2>&1 | tail -20
gcloud run jobs delete create-admin-final --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Concluído! Teste o login:"
echo "https://monpec-29862706245.us-central1.run.app/login/"








