#!/bin/bash
# Atualizar serviço Cloud Run com variáveis do banco de dados

echo "🔧 Atualizando serviço Cloud Run com variáveis do banco"
echo "======================================================="
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")

echo "Connection Name: $CONNECTION_NAME"
echo ""

# Obter variáveis atuais do serviço
echo "▶ Obtendo variáveis atuais do serviço..."
CURRENT_ENV=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)")

# Atualizar serviço adicionando variáveis do banco
echo "▶ Atualizando serviço com variáveis do banco..."
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --add-env-vars "DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!SenhaSegura,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --add-cloudsql-instances $CONNECTION_NAME

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Serviço atualizado com sucesso!"
    echo ""
    echo "▶ Aguardando nova revisão ficar pronta..."
    sleep 10
    
    echo ""
    echo "✅ Agora execute o job para criar o admin novamente:"
    echo ""
    echo "gcloud run jobs execute create-admin --region $REGION --wait"
else
    echo ""
    echo "❌ Erro ao atualizar serviço!"
    exit 1
fi








