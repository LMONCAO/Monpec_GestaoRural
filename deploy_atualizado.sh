#!/bin/bash
# SCRIPT DE DEPLOY MONPEC - VERSÃO ATUALIZADA
# Execute no Google Cloud Shell

echo "🚀 Iniciando deploy MONPEC..."

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Build da imagem
echo "🔨 Fazendo build da imagem..."
gcloud builds submit . --tag gcr.io/monpec-sistema-rural/monpec:latest --timeout=20m

# Deploy do serviço
echo "🚀 Fazendo deploy..."
gcloud run deploy monpec \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it,DEBUG=False" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --min-instances=1 \
  --port=8080

# Executar migrações
echo "🗄️ Executando migrações..."
gcloud run jobs create migrate-monpec-complete \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,--noinput" \
  --memory=2Gi \
  --cpu=1 \
  --max-retries=3 \
  --task-timeout=600

gcloud run jobs execute migrate-monpec-complete --region=us-central1 --wait

# Popular dados de produção
echo "📊 Populando dados de produção..."
gcloud run jobs create populate-monpec-data \
  --image gcr.io/monpec-sistema-rural/monpec:latest \
  --region us-central1 \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=R72dONWK0vl4yZfpEXwHVr8it" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="popular_dados_producao.py" \
  --memory=2Gi \
  --cpu=1 \
  --max-retries=3 \
  --task-timeout=600

gcloud run jobs execute populate-monpec-data --region=us-central1 --wait

# Verificar status
echo "✅ Verificando status..."
URL=$(gcloud run services describe monpec --region=us-central1 --format="value(status.url)")
echo "🌐 Serviço disponível em: $URL"

echo "🎉 Deploy concluído com sucesso!"
echo "📱 Landing page: $URL"
echo "🔐 Admin: $URL/admin/"
