#!/bin/bash
# FINAL DEPLOY MONPEC - SCRIPT COMPLETO
# Copie e cole tudo no Cloud Shell

echo "========================================="
echo "🚀 FINAL DEPLOY MONPEC COMPLETO"
echo "========================================="

# Configurações finais
IMAGE="gcr.io/monpec-sistema-rural/monpec:latest"
REGION="us-central1"
SERVICE="monpec"
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_HOST=34.9.51.178,DB_PORT=5432,DB_NAME=monpec-db,DB_USER=postgres,DB_PASSWORD=L6171r12@@jjms,DEBUG=False,SECRET_KEY=django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

echo "1️⃣ LIMPANDO JOBS ANTIGOS..."
gcloud run jobs delete migrate-final --region=$REGION --quiet 2>/dev/null || echo "Job migrate-final não existia"
gcloud run jobs delete populate-final --region=$REGION --quiet 2>/dev/null || echo "Job populate-final não existia"
gcloud run jobs delete reset-db-final --region=$REGION --quiet 2>/dev/null || echo "Job reset-db-final não existia"

echo "2️⃣ RESETANDO BANCO DE DADOS..."
gcloud run jobs create reset-db-final \
  --image $IMAGE \
  --region $REGION \
  --set-env-vars="$ENV_VARS" \
  --command="python" \
  --args="manage.py,reset_db" \
  --memory=4Gi \
  --cpu=2 \
  --max-retries=1 \
  --task-timeout=3600

echo "Executando reset..."
gcloud run jobs execute reset-db-final --region=$REGION --wait

echo "3️⃣ APLICANDO MIGRAÇÕES..."
gcloud run jobs create migrate-final \
  --image $IMAGE \
  --region $REGION \
  --set-env-vars="$ENV_VARS" \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --memory=4Gi \
  --cpu=2 \
  --max-retries=1 \
  --task-timeout=1800

echo "Executando migrações..."
gcloud run jobs execute migrate-final --region=$REGION --wait

echo "4️⃣ POPULANDO DADOS..."
gcloud run jobs create populate-final \
  --image $IMAGE \
  --region $REGION \
  --set-env-vars="$ENV_VARS" \
  --command="python" \
  --args="popular_dados_producao.py" \
  --memory=4Gi \
  --cpu=2 \
  --max-retries=1 \
  --task-timeout=1800

echo "Executando população..."
gcloud run jobs execute populate-final --region=$REGION --wait

echo "5️⃣ ATUALIZANDO SERVIÇO..."
gcloud run services update $SERVICE \
  --region=$REGION \
  --set-env-vars="$ENV_VARS" \
  --memory=4Gi \
  --cpu=2 \
  --timeout=300

echo "6️⃣ TESTANDO SISTEMA..."
echo "=== VERIFICANDO SISTEMA ==="
curl -I https://monpec-29862706245.us-central1.run.app/

echo ""
echo "=== TESTANDO LANDING PAGE ==="
curl -s https://monpec-29862706245.us-central1.run.app/ | head -10

echo ""
echo "========================================="
echo "🎉 DEPLOY CONCLUÍDO!"
echo "========================================="
echo ""
echo "🌐 Landing Page: https://monpec-29862706245.us-central1.run.app/"
echo "🔐 Admin: https://monpec-29862706245.us-central1.run.app/admin/"
echo "📊 Dashboard: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/"
echo "📅 Planejamento: https://monpec-29862706245.us-central1.run.app/propriedade/5/pecuaria/planejamento/"
echo ""
echo "👤 LOGIN ADMIN:"
echo "Usuário: admin"
echo "Senha: [sua senha atual]"
echo ""
echo "========================================="