#!/bin/bash
# Solução completa final: migrações + admin
# Desabilita history expansion para evitar erro com ! na senha

set +H  # Desabilita history expansion
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "🔧 Configurando variáveis..."
echo ""

# PASSO 1: Executar migrações até 0071 (cria tabela Produto)
echo "▶ PASSO 1: Executando migrações até 0071 (cria tabela Produto)..."
gcloud run jobs create run-migrations-step1 \
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

echo "Executando job..."
gcloud run jobs execute run-migrations-step1 --region us-central1 --wait 2>&1 | tail -50
gcloud run jobs delete run-migrations-step1 --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ PASSO 2: Executando todas as migrações restantes..."

# PASSO 2: Executar todas as migrações
gcloud run jobs create run-migrations-step2 \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args manage.py,migrate,--noinput \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo "Executando job..."
gcloud run jobs execute run-migrations-step2 --region us-central1 --wait 2>&1 | tail -50
gcloud run jobs delete run-migrations-step2 --region us-central1 --quiet 2>&1 || true

echo ""
echo "▶ PASSO 3: Criando admin..."

# PASSO 3: Criar admin (usando script Python inline sem problemas de bash)
gcloud run jobs create create-admin-step3 \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args -c,"import os;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');import django;django.setup();from django.contrib.auth import get_user_model;User=get_user_model();u,created=User.objects.get_or_create(username='admin',defaults={'email':'admin@monpec.com.br','is_superuser':True,'is_staff':True,'is_active':True});u.set_password('L6171r12@@');u.is_superuser=True;u.is_staff=True;u.is_active=True;u.save();print('✅ Admin criado/atualizado!')" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo "Executando job..."
gcloud run jobs execute create-admin-step3 --region us-central1 --wait 2>&1 | tail -20
gcloud run jobs delete create-admin-step3 --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ CONCLUÍDO!"
echo ""
echo "🔐 Credenciais de acesso:"
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








