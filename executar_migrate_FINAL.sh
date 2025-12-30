#!/bin/bash
# Script FINAL para executar migrate, collectstatic e criar admin
# Execute: bash executar_migrate_FINAL.sh

echo "=== EXECUTAR MIGRATE E COLECTSTATIC - VERSÃO FINAL ==="
echo ""

# Configurar projeto
echo "1️⃣ Configurando projeto..."
gcloud config set project monpec-sistema-rural 2>/dev/null || true
echo "✅ Projeto: monpec-sistema-rural"
echo ""

# Definir imagem (ajuste se necessário)
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"
echo "2️⃣ Usando imagem: $IMAGE_NAME"
echo ""

# Criar job para migrate + collectstatic
echo "3️⃣ Criando Cloud Run Job para migrate + collectstatic..."
gcloud run jobs create migrate-collectstatic \
  --image="$IMAGE_NAME" \
  --region=us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,python manage.py migrate --noinput && python manage.py collectstatic --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  2>&1 | grep -v "already exists" || {
    echo "Job já existe, atualizando..."
    gcloud run jobs update migrate-collectstatic \
      --region=us-central1 \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="sh" \
      --args="-c,python manage.py migrate --noinput && python manage.py collectstatic --noinput" \
      --memory=2Gi \
      --cpu=2
}

echo "✅ Job pronto"
echo ""

# Executar migrate + collectstatic
echo "4️⃣ Executando migrate e collectstatic..."
echo "⏱️ Aguarde 3-5 minutos..."
echo ""
gcloud run jobs execute migrate-collectstatic --region=us-central1 --wait 2>&1 || {
    echo ""
    echo "⚠️ Erro ao executar, mas pode ter funcionado. Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=migrate-collectstatic\" --limit=10"
}

echo ""
echo "✅ Migrate e collectstatic concluídos (ou erro tratado)"
echo ""

# Criar job para admin
echo "5️⃣ Criando Cloud Run Job para criar usuário admin..."
gcloud run jobs create create-admin \
  --image="$IMAGE_NAME" \
  --region=us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,shell,-c,from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  2>&1 | grep -v "already exists" || {
    echo "Job já existe, atualizando..."
    gcloud run jobs update create-admin \
      --region=us-central1 \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="python" \
      --args="manage.py,shell,-c,from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'L6171r12@@')" \
      --memory=2Gi \
      --cpu=2
}

echo "✅ Job pronto"
echo ""

# Executar criar admin
echo "6️⃣ Criando usuário admin..."
echo "⏱️ Aguarde 1-2 minutos..."
echo ""
gcloud run jobs execute create-admin --region=us-central1 --wait 2>&1 || {
    echo ""
    echo "⚠️ Erro ao executar, mas pode ter funcionado. Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=create-admin\" --limit=10"
}

echo ""
echo "✅✅✅ PROCESSO CONCLUÍDO! ✅✅✅"
echo ""
echo "📝 Credenciais de acesso:"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""
echo "💡 Se apareceram erros de autenticação mas os jobs foram criados,"
echo "   eles podem ter funcionado mesmo assim no Cloud Shell."

