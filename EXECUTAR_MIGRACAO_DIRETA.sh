#!/bin/bash
# Alternativa: Executar migração diretamente no serviço (sem job)

SERVICE_NAME="monpec"
REGION="us-central1"

echo "========================================"
echo "🔄 Executar Migração Diretamente"
echo "========================================"
echo ""
echo "Esta é uma alternativa se o job continuar falhando."
echo "Vamos executar as migrações diretamente no serviço."
echo ""

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    echo "❌ Serviço não encontrado"
    exit 1
fi

echo "Serviço: $SERVICE_URL"
echo ""
echo "Opções:"
echo ""
echo "1. Executar via Cloud Shell (recomendado):"
echo "   gcloud run services proxy $SERVICE_NAME --region $REGION --port 8080"
echo "   # Em outro terminal:"
echo "   curl -X POST http://localhost:8080/admin/migrate/ || python manage.py migrate"
echo ""
echo "2. Executar via Cloud Run Jobs (tentar novamente):"
echo "   SERVICE_ENV=\$(gcloud run services describe $SERVICE_NAME --region $REGION --format=\"value(spec.template.spec.containers[0].env)\")"
echo "   gcloud run jobs update migrate-monpec --region $REGION --update-env-vars \"\$SERVICE_ENV\""
echo "   gcloud run jobs execute migrate-monpec --region $REGION --wait"
echo ""
echo "3. Ver logs detalhados primeiro:"
echo "   ./VER_LOGS_ERRO.sh"
echo ""


