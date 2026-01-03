#!/bin/bash
# Deploy FINAL após migrations aplicadas
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔄 Fazendo deploy do serviço (com configurações otimizadas)"
echo "============================================================"
echo ""

# Ver logs da última tentativa
echo "📋 Verificando logs da última tentativa..."
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=10 --format="value(textPayload)" 2>/dev/null | tail -5

echo ""
echo "📦 Fazendo deploy..."
gcloud run deploy monpec \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --allow-unauthenticated \
  --port=8080

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
    echo "============================================================"
    echo ""
    echo "🌐 Acesse o sistema em:"
    echo "   https://monpec-fzzfjppzva-uc.a.run.app/login/"
    echo ""
    echo "💡 Agora você pode criar o usuário admin:"
    echo "   Execute o script: CRIAR_ADMIN_CLOUD_SHELL.sh"
    echo ""
else
    echo ""
    echo "❌ Deploy falhou. Verificando logs..."
    echo ""
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
    echo ""
    echo "💡 Possíveis soluções:"
    echo "   1. Verifique se a imagem está correta"
    echo "   2. Verifique se o banco está acessível"
    echo "   3. Tente aumentar o timeout ou memória"
fi
