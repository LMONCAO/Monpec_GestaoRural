#!/bin/bash
# Solução: verificar se migração 0071 realmente criou a tabela e forçar se necessário

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "▶ Verificando estado completo..."

# Verificar se migração está registrada E se tabela existe
gcloud run jobs create check-full-status \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ['DJANGO_SETTINGS_MODULE']='sistema_rural.settings_gcp';import django;django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"SELECT COUNT(*) FROM django_migrations WHERE app='gestao_rural' AND name='0071_adicionar_produtos_cadastro_fiscal';\");mig_count=cursor.fetchone()[0];cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_produto');\");table_exists=cursor.fetchone()[0];print(f'Migração 0071 registrada: {mig_count > 0}');print(f'Tabela gestao_rural_produto existe: {table_exists}');if mig_count > 0 and not table_exists: print('⚠️ PROBLEMA: Migração registrada mas tabela não existe!');exit(1);exit(0)" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

STATUS_OUTPUT=$(gcloud run jobs execute check-full-status --region us-central1 --wait 2>&1)
echo "$STATUS_OUTPUT" | tail -20
gcloud run jobs delete check-full-status --region us-central1 --quiet 2>&1 || true

# Se a migração está registrada mas a tabela não existe, precisamos remover o registro e reaplicar
if echo "$STATUS_OUTPUT" | grep -q "PROBLEMA"; then
    echo ""
    echo "▶ Removendo registro da migração 0071 para reaplicar..."
    
    gcloud run jobs create remove-migration-71 \
      --image gcr.io/$PROJECT_ID/monpec \
      --region us-central1 \
      --command python \
      --args -c,"import os;os.environ['DJANGO_SETTINGS_MODULE']='sistema_rural.settings_gcp';import django;django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"DELETE FROM django_migrations WHERE app='gestao_rural' AND name='0071_adicionar_produtos_cadastro_fiscal';\");print('✅ Registro da migração 0071 removido');exit(0)" \
      --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
      --set-cloudsql-instances $CONNECTION_NAME \
      --max-retries 1 \
      --task-timeout 300 \
      --memory 512Mi \
      --cpu 1 2>&1 | grep -v "already exists" || true
    
    gcloud run jobs execute remove-migration-71 --region us-central1 --wait 2>&1 | tail -10
    gcloud run jobs delete remove-migration-71 --region us-central1 --quiet 2>&1 || true
    
    echo ""
    echo "▶ Reaplicando migração 0071..."
    
    gcloud run jobs create reapply-0071 \
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
    
    REAPPLY_OUTPUT=$(gcloud run jobs execute reapply-0071 --region us-central1 --wait 2>&1)
    echo "$REAPPLY_OUTPUT" | tail -100
    gcloud run jobs delete reapply-0071 --region us-central1 --quiet 2>&1 || true
fi

echo ""
echo "▶ Verificando novamente se tabela existe..."

gcloud run jobs create verify-table-final \
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

VERIFY_OUTPUT=$(gcloud run jobs execute verify-table-final --region us-central1 --wait 2>&1)
echo "$VERIFY_OUTPUT" | tail -10
gcloud run jobs delete verify-table-final --region us-central1 --quiet 2>&1 || true

if echo "$VERIFY_OUTPUT" | grep -q "ainda não existe"; then
    echo ""
    echo "❌ Tabela ainda não foi criada. Verifique os logs da migração 0071."
    exit 1
fi

echo ""
echo "✅ Tabela criada! Continuando com migrações restantes..."

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

MIG_ALL_OUTPUT=$(gcloud run jobs execute run-all-remaining-migrations --region us-central1 --wait 2>&1)
echo "$MIG_ALL_OUTPUT" | tail -100
gcloud run jobs delete run-all-remaining-migrations --region us-central1 --quiet 2>&1 || true

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








