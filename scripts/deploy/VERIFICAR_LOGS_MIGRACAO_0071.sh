#!/bin/bash
# Verificar logs da migração 0071 para entender por que a tabela não foi criada

PROJECT_ID=$(gcloud config get-value project)

echo "🔍 Verificando logs da migração 0071..."
echo ""

gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=apply-0071-specific AND resource.labels.location=us-central1" --limit 200 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -200

echo ""
echo "================================================================================"
echo ""
echo "🔍 Verificando estado das migrações no banco..."

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
DB_PASS='Monpec2025!SenhaSegura'

gcloud run jobs create check-migrations-status \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ['DJANGO_SETTINGS_MODULE']='sistema_rural.settings_gcp';import django;django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"SELECT app, name, applied FROM django_migrations WHERE app='gestao_rural' ORDER BY id DESC LIMIT 10;\");migrations=cursor.fetchall();print('Últimas 10 migrações de gestao_rural:');for m in migrations: print(f'  {m[0]}.{m[1]} - Aplicada: {m[2]}');cursor.execute(\"SELECT COUNT(*) FROM django_migrations WHERE app='gestao_rural' AND name='0071_adicionar_produtos_cadastro_fiscal';\");count=cursor.fetchone()[0];print(f'\nMigração 0071 está registrada: {count > 0}');exit(0)" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

gcloud run jobs execute check-migrations-status --region us-central1 --wait 2>&1 | tail -50
gcloud run jobs delete check-migrations-status --region us-central1 --quiet 2>&1 || true








