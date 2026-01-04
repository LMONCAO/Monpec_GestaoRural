#!/bin/bash
# Verificar status do deploy e testar sistema
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔍 Verificando status do serviço"
echo "============================================================"
echo ""

# Verificar status do serviço
echo "📊 Status do serviço:"
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url,status.latestReadyRevisionName,status.conditions[0].status)"

echo ""
echo "============================================================"
echo "🔍 Verificando logs recentes (últimos 5 minutos)"
echo "============================================================"
echo ""

# Verificar se há erros recentes
ERRORS=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
  --limit=5 \
  --format="value(textPayload)" \
  --freshness=5m)

if [ -z "$ERRORS" ]; then
    echo "✅ Nenhum erro encontrado nos últimos 5 minutos!"
else
    echo "⚠️  Erros encontrados:"
    echo "$ERRORS"
fi

echo ""
echo "============================================================"
echo "🌐 URLs do sistema:"
echo "============================================================"
echo ""
echo "Login: https://monpec-29862706245.us-central1.run.app/login/"
echo "Home: https://monpec-29862706245.us-central1.run.app/"
echo ""

echo "============================================================"
echo "✅ Próximos passos:"
echo "============================================================"
echo ""
echo "1. Acesse: https://monpec-29862706245.us-central1.run.app/login/"
echo "2. Teste se a página de login carrega sem erro 500"
echo "3. Se ainda houver erro, execute:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR\" --limit=10 --format=\"value(textPayload)\" --freshness=5m"
echo ""


