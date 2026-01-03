#!/bin/bash
# Solução definitiva: aplicar migração 0071 especificamente e depois todas as outras

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "▶ PASSO 1: Verificando estado da migração 0071..."

# Verificar se 0071 está aplicada
gcloud run jobs create check-0071-status \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ['DJANGO_SETTINGS_MODULE']='sistema_rural.settings_gcp';import django;django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"SELECT COUNT(*) FROM django_migrations WHERE app='gestao_rural' AND name='0071_adicionar_produtos_cadastro_fiscal';\");count=cursor.fetchone()[0];cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_produto');\");table_exists=cursor.fetchone()[0];print(f'Migração 0071 aplicada: {count > 0}');print(f'Tabela gestao_rural_produto existe: {table_exists}');exit(0)" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

CHECK_OUTPUT=$(gcloud run jobs execute check-0071-status --region us-central1 --wait 2>&1)
echo "$CHECK_OUTPUT" | tail -20
gcloud run jobs delete check-0071-status --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ PASSO 2: Aplicando migração 0071 especificamente..."

# Aplicar migração 0071 especificamente
gcloud run jobs create apply-0071-specific \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,migrate,gestao_rural,0071_adicionar_produtos_cadastro_fiscal,--verbosity=2 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo "Executando migração 0071..."
MIG71_OUTPUT=$(gcloud run jobs execute apply-0071-specific --region us-central1 --wait 2>&1)
echo "$MIG71_OUTPUT" | tail -100

# Verificar se houve erro
if echo "$MIG71_OUTPUT" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Erro ao aplicar migração 0071. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=apply-0071-specific AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -100
    gcloud run jobs delete apply-0071-specific --region us-central1 --quiet 2>&1 || true
    exit 1
fi

gcloud run jobs delete apply-0071-specific --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Migração 0071 aplicada!"
echo ""
echo "▶ PASSO 3: Verificando se tabela foi criada..."

# Verificar se tabela existe agora
gcloud run jobs create verify-table-created \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ['DJANGO_SETTINGS_MODULE']='sistema_rural.settings_gcp';import django;django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_produto');\");exists=cursor.fetchone()[0];print('✅ Tabela gestao_rural_produto criada!' if exists else '❌ Tabela ainda não existe!');exit(0 if exists else 1)" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

VERIFY_OUTPUT=$(gcloud run jobs execute verify-table-created --region us-central1 --wait 2>&1)
echo "$VERIFY_OUTPUT" | tail -10
gcloud run jobs delete verify-table-created --region us-central1 --quiet 2>&1 || true

if echo "$VERIFY_OUTPUT" | grep -q "ainda não existe"; then
    echo ""
    echo "❌ Tabela não foi criada. Abortando..."
    exit 1
fi

echo ""
echo "▶ PASSO 4: Executando todas as migrações restantes..."

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

echo "Executando migrações restantes..."
MIG_ALL_OUTPUT=$(gcloud run jobs execute run-all-remaining-migrations --region us-central1 --wait 2>&1)
echo "$MIG_ALL_OUTPUT" | tail -100

if echo "$MIG_ALL_OUTPUT" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Erro nas migrações. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=run-all-remaining-migrations AND resource.labels.location=us-central1" --limit 100 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -100
    gcloud run jobs delete run-all-remaining-migrations --region us-central1 --quiet 2>&1 || true
    exit 1
fi

gcloud run jobs delete run-all-remaining-migrations --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Migrações concluídas!"
echo ""
echo "▶ PASSO 5: Criando admin..."

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
echo "✅✅✅ TUDO CONCLUÍDO COM SUCESSO! ✅✅✅"
echo ""
echo "🔐 CREDENCIAIS DE ACESSO:"
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








