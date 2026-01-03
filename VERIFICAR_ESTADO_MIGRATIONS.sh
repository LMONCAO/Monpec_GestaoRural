#!/bin/bash
# Verificar estado real das migrations no banco
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📊 Verificando estado das migrations no banco"
echo "============================================================"
echo ""

gcloud run jobs delete verificar-migrations-estado --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create verificar-migrations-estado \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute('SELECT COUNT(*) FROM django_migrations WHERE app=\\'gestao_rural\\'');total=cursor.fetchone()[0];cursor.execute('SELECT name FROM django_migrations WHERE app=\\'gestao_rural\\' ORDER BY id DESC LIMIT 5');ultimas=[r[0] for r in cursor.fetchall()];print(f'Total de migrations registradas para gestao_rural: {total}');print('Últimas 5 migrations aplicadas:');for m in ultimas: print(f'  - {m}');from django.core.management import call_command;print('\\nVerificando migrations pendentes...');import sys;from io import StringIO;old_stdout=sys.stdout;sys.stdout=StringIO();try:call_command('migrate','--plan');output=sys.stdout.getvalue();sys.stdout=old_stdout;pendentes=[l for l in output.split('\\n') if '[ ]' in l];print(f'Migrations pendentes: {len(pendentes)}');if len(pendentes)>0:print('Primeiras 10:');[print(f'  {p}') for p in pendentes[:10]];else:print('✅ Nenhuma migration pendente!');except Exception as e:sys.stdout=old_stdout;print(f'Erro: {e}')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute verificar-migrations-estado --region=$REGION --wait

gcloud run jobs delete verificar-migrations-estado --region=$REGION --quiet 2>/dev/null || true
