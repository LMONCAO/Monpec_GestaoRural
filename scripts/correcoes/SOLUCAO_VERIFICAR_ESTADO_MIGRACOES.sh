#!/bin/bash
# Verificar estado real das migrações e executar apenas as que faltam

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "🔍 Verificando estado REAL das migrações..."

# Verificar quais migrações já foram aplicadas
gcloud run jobs create check-migrations-real \
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
OUTPUT=$(gcloud run jobs execute check-migrations-real --region us-central1 --wait 2>&1)
echo "$OUTPUT" | grep -A 200 "gestao_rural" || echo "$OUTPUT" | tail -100

gcloud run jobs delete check-migrations-real --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ Verificando se a tabela gestao_rural_produto existe..."

# Verificar se a tabela existe diretamente no banco
gcloud run jobs create check-table-exists \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ['DJANGO_SETTINGS_MODULE']='sistema_rural.settings_gcp';import django;django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_produto');\");exists=cursor.fetchone()[0];print('✅ Tabela gestao_rural_produto existe!' if exists else '❌ Tabela gestao_rural_produto NÃO existe!');exit(0 if exists else 1)" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

TABLE_OUTPUT=$(gcloud run jobs execute check-table-exists --region us-central1 --wait 2>&1)
echo "$TABLE_OUTPUT" | tail -20
gcloud run jobs delete check-table-exists --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Verificação concluída!"








