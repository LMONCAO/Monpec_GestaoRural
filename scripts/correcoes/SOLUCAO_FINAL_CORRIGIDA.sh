#!/bin/bash
# Solução final corrigida: verifica estado e executa migrações na ordem correta

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "▶ Verificando se migração 0071 foi aplicada..."

# Verificar se a migração 0071 está aplicada
gcloud run jobs create check-71-applied \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ['DJANGO_SETTINGS_MODULE']='sistema_rural.settings_gcp';import django;django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"SELECT COUNT(*) FROM django_migrations WHERE app='gestao_rural' AND name='0071_adicionar_produtos_cadastro_fiscal';\");count=cursor.fetchone()[0];print('✅ Migração 0071 aplicada!' if count > 0 else '❌ Migração 0071 NÃO aplicada!');exit(0 if count > 0 else 1)" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

CHECK_OUTPUT=$(gcloud run jobs execute check-71-applied --region us-central1 --wait 2>&1)
echo "$CHECK_OUTPUT" | tail -10
gcloud run jobs delete check-71-applied --region us-central1 --quiet 2>&1 || true

# Se a migração 0071 não foi aplicada, aplicar primeiro
if echo "$CHECK_OUTPUT" | grep -q "NÃO aplicada"; then
    echo ""
    echo "▶ Aplicando migração 0071 primeiro..."
    gcloud run jobs create apply-71-first \
      --image gcr.io/$PROJECT_ID/monpec \
      --region us-central1 \
      --command python \
      --args manage.py,migrate,gestao_rural,0071_adicionar_produtos_cadastro_fiscal \
      --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
      --set-cloudsql-instances $CONNECTION_NAME \
      --max-retries 1 \
      --task-timeout 600 \
      --memory 1Gi \
      --cpu 1 2>&1 | grep -v "already exists" || true
    
    gcloud run jobs execute apply-71-first --region us-central1 --wait 2>&1 | tail -50
    gcloud run jobs delete apply-71-first --region us-central1 --quiet 2>&1 || true
fi

echo ""
echo "▶ Executando todas as migrações restantes..."

# Executar todas as migrações (Django vai pular as que já foram aplicadas)
gcloud run jobs create run-all-migrations-final \
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

MIGRATION_OUTPUT=$(gcloud run jobs execute run-all-migrations-final --region us-central1 --wait 2>&1)
echo "$MIGRATION_OUTPUT" | tail -100

if echo "$MIGRATION_OUTPUT" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Erro nas migrações. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=run-all-migrations-final AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -100
    gcloud run jobs delete run-all-migrations-final --region us-central1 --quiet 2>&1 || true
    exit 1
fi

gcloud run jobs delete run-all-migrations-final --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Migrações concluídas!"
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

ADMIN_OUTPUT=$(gcloud run jobs execute create-admin-final --region us-central1 --wait 2>&1)
echo "$ADMIN_OUTPUT" | tail -30
gcloud run jobs delete create-admin-final --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅✅✅ TUDO CONCLUÍDO! ✅✅✅"
echo ""
echo "🔐 CREDENCIAIS:"
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








