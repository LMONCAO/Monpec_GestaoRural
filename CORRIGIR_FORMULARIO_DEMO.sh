#!/bin/bash
# Script para corrigir formulário de demonstração - USANDO COMANDOS INLINE (não precisa de manage.py no PATH)

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:monpec-db"

echo "============================================================"
echo "CORRIGINDO FORMULÁRIO DE DEMONSTRAÇÃO"
echo "============================================================"
echo ""

gcloud config set project $PROJECT_ID

echo "1️⃣ Aplicando migrações (usando comando Python inline)..."
gcloud run jobs delete aplicar-migracoes-demo --region=$REGION --quiet 2>/dev/null || true

# Usar comando Python inline que não precisa do manage.py no PATH
gcloud run jobs create aplicar-migracoes-demo \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py migrate --noinput" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

echo "⏱️  Executando migrações (pode levar 2-3 minutos)..."
gcloud run jobs execute aplicar-migracoes-demo --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo "✅ Migrações aplicadas com sucesso!"
else
    echo "❌ Erro ao aplicar migrações. Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migracoes-demo\" --limit=50"
    exit 1
fi

echo ""
echo "2️⃣ Verificando se tabela UsuarioAtivo foi criada..."
gcloud run jobs delete verificar-tabela-demo --region=$REGION --quiet 2>/dev/null || true

# Verificar usando comando Python inline
gcloud run jobs create verificar-tabela-demo \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="-c,import os; os.chdir('/app'); os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp'); import django; django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%usuarioativo%'\"); result = cursor.fetchone(); print('✅ Tabela encontrada:', result[0] if result else '❌ Tabela NAO encontrada')" \
  --memory=2Gi \
  --cpu=2

echo "⏱️  Verificando tabela..."
gcloud run jobs execute verificar-tabela-demo --region=$REGION --wait
gcloud run jobs delete verificar-tabela-demo --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "============================================================"
echo "✅ Processo concluído!"
echo "============================================================"
echo ""
echo "📝 Próximos passos:"
echo "   1. Teste o formulário de demonstração novamente em: https://monpec.com.br"
echo "   2. Se ainda houver erro, verifique os logs:"
echo "      gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND textPayload=~'demonstração'\" --limit=50"
echo ""

# Limpar job
gcloud run jobs delete aplicar-migracoes-demo --region=$REGION --quiet 2>/dev/null || true

echo "🗑️  Jobs temporários removidos."
