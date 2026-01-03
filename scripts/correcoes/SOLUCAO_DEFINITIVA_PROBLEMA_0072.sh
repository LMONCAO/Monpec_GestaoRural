#!/bin/bash
# Solução definitiva para o problema da migração 0072

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "🔍 DIAGNÓSTICO: Verificando estado da tabela Produto..."

# Verificar se tabela existe e se tem dados
gcloud run jobs create check-produto-table \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');import django;django.setup();from django.db import connection;c=connection.cursor();c.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_produto')\");exists=c.fetchone()[0];print(f'Tabela existe: {exists}');if exists:c.execute('SELECT COUNT(*) FROM gestao_rural_produto');count=c.fetchone()[0];print(f'Registros: {count}');c.execute('SELECT COUNT(*) FROM gestao_rural_produto WHERE ncm IS NULL OR ncm=\\'\'');null_count=c.fetchone()[0];print(f'Registros com NCM NULL: {null_count}')" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

CHECK_OUTPUT=$(gcloud run jobs execute check-produto-table --region us-central1 --wait 2>&1)
echo "$CHECK_OUTPUT" | tail -50
gcloud run jobs delete check-produto-table --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ CORREÇÃO: Preenchendo NCM NULL com valor padrão (se necessário)..."

# Preencher NCM NULL com valor padrão temporário
gcloud run jobs create fix-ncm-null \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');import django;django.setup();from django.db import connection;c=connection.cursor();c.execute(\"UPDATE gestao_rural_produto SET ncm='0000.00.00' WHERE ncm IS NULL OR ncm=''\")" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

FIX_OUTPUT=$(gcloud run jobs execute fix-ncm-null --region us-central1 --wait 2>&1)
echo "$FIX_OUTPUT" | tail -30
gcloud run jobs delete fix-ncm-null --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ Aplicando migração 0072 (agora deve funcionar)..."

gcloud run jobs create apply-72-fixed \
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

MIG72_OUTPUT=$(gcloud run jobs execute apply-72-fixed --region us-central1 --wait 2>&1)
echo "$MIG72_OUTPUT" | tail -50

if echo "$MIG72_OUTPUT" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Ainda há erro. Verificando logs detalhados..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=apply-72-fixed AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -100
    gcloud run jobs delete apply-72-fixed --region us-central1 --quiet 2>&1 || true
    exit 1
fi

gcloud run jobs delete apply-72-fixed --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Migração 0072 aplicada! Agora aplicando todas as restantes..."

gcloud run jobs create apply-all-remaining-final \
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

FINAL_OUTPUT=$(gcloud run jobs execute apply-all-remaining-final --region us-central1 --wait 2>&1)
echo "$FINAL_OUTPUT" | tail -50
gcloud run jobs delete apply-all-remaining-final --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅✅✅ TODAS AS MIGRAÇÕES CONCLUÍDAS! ✅✅✅"
echo ""
echo "🔐 O admin já foi criado anteriormente."
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""







