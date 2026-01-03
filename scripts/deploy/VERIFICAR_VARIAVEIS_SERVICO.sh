#!/bin/bash
# Verificar se o serviço tem as variáveis corretas do banco

echo "🔍 Verificando variáveis do serviço Cloud Run"
echo "=============================================="
echo ""

# Ver todas as variáveis do serviço
gcloud run services describe monpec --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | grep -E "(DB_|CLOUD_SQL|GOOGLE_CLOUD_PROJECT)"

echo ""
echo "▶ Verificando se CLOUD_SQL_CONNECTION_NAME está configurado..."
CLOUD_SQL=$(gcloud run services describe monpec --region us-central1 \
  --format="value(spec.template.spec.containers[0].env)" | grep CLOUD_SQL_CONNECTION_NAME)

if [ -z "$CLOUD_SQL" ]; then
    echo "❌ CLOUD_SQL_CONNECTION_NAME NÃO está configurado no serviço!"
    echo ""
    echo "Execute este comando para adicionar:"
    echo ""
    CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
    PROJECT_ID=$(gcloud config get-value project)
    echo "DB_PASS='Monpec2025!SenhaSegura'"
    echo "gcloud run services update monpec --region us-central1 \\"
    echo "  --update-env-vars \"DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=\$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID\" \\"
    echo "  --add-cloudsql-instances $CONNECTION_NAME"
else
    echo "✅ Variáveis do banco estão configuradas"
fi








