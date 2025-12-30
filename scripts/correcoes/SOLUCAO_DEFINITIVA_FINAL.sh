#!/bin/bash
# Solução definitiva: executa migrações na ordem correta e cria admin usando arquivo

set +H
set -e

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

echo "▶ PASSO 1: Executando migrações até 0071 (cria tabela Produto)..."

# Executar especificamente até 0071
gcloud run jobs create run-migrations-to-71 \
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
OUTPUT1=$(gcloud run jobs execute run-migrations-to-71 --region us-central1 --wait 2>&1)
echo "$OUTPUT1" | tail -50

# Verificar se houve erro
if echo "$OUTPUT1" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Erro no PASSO 1. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=run-migrations-to-71 AND resource.labels.location=us-central1" --limit 50 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -80
    gcloud run jobs delete run-migrations-to-71 --region us-central1 --quiet 2>&1 || true
    exit 1
fi

gcloud run jobs delete run-migrations-to-71 --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ PASSO 1 concluído!"
echo ""
echo "▶ PASSO 2: Executando todas as migrações restantes..."

# Executar todas as migrações restantes
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

echo "Executando job..."
OUTPUT2=$(gcloud run jobs execute run-all-migrations --region us-central1 --wait 2>&1)
echo "$OUTPUT2" | tail -50

# Verificar se houve erro
if echo "$OUTPUT2" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Erro no PASSO 2. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=run-all-migrations AND resource.labels.location=us-central1" --limit 50 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -80
    gcloud run jobs delete run-all-migrations --region us-central1 --quiet 2>&1 || true
    exit 1
fi

gcloud run jobs delete run-all-migrations --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ PASSO 2 concluído!"
echo ""
echo "▶ PASSO 3: Criando admin usando arquivo criar_admin_producao.py..."

# Criar admin usando o arquivo Python (mais confiável que comando inline)
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

echo "Executando job..."
OUTPUT3=$(gcloud run jobs execute create-admin-final --region us-central1 --wait 2>&1)
echo "$OUTPUT3" | tail -50

# Verificar se houve erro
if echo "$OUTPUT3" | grep -q "failed\|ERROR"; then
    echo ""
    echo "❌ Erro no PASSO 3. Verificando logs..."
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=create-admin-final AND resource.labels.location=us-central1" --limit 50 --format="table(timestamp,textPayload)" --project=$PROJECT_ID | head -80
    gcloud run jobs delete create-admin-final --region us-central1 --quiet 2>&1 || true
    exit 1
fi

gcloud run jobs delete create-admin-final --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅✅✅ TUDO CONCLUÍDO COM SUCESSO! ✅✅✅"
echo ""
echo "🔐 CREDENCIAIS DE ACESSO:"
echo "   URL: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""








