#!/bin/bash
# Script para executar NO GOOGLE CLOUD SHELL
# Copie e cole este script inteiro no Cloud Shell

set -e

echo ""
echo "========================================"
echo "  BUILD E DEPLOY AUTOMÁTICO - MONPEC"
echo "========================================"
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
CONNECTION_NAME="monpec-sistema-rural:us-central1:monpec-db"
DB_PASSWORD="R72dONWK0vl4yZfpEXwHVr8it"

# Configurar projeto
echo "▶ Configurando projeto..."
gcloud config set project "$PROJECT_ID" --quiet
echo "✓ Projeto configurado"
echo ""

# 1. Build da imagem
echo "▶ Fazendo build da imagem Docker..."
echo "   Isso pode levar 5-10 minutos..."
echo ""

gcloud builds submit . --tag "${IMAGE_NAME}:latest" --timeout=20m

if [ $? -eq 0 ]; then
    echo "✓ Build concluído com sucesso!"
else
    echo "✗ Erro no build da imagem!"
    exit 1
fi
echo ""

# 2. Deploy no Cloud Run
echo "▶ Fazendo deploy no Cloud Run..."
echo ""

gcloud run deploy "$SERVICE_NAME" \
    --image "${IMAGE_NAME}:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=${CONNECTION_NAME},DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=${DB_PASSWORD},DEBUG=False" \
    --add-cloudsql-instances="$CONNECTION_NAME" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1 \
    --port=8080 \
    --quiet

if [ $? -eq 0 ]; then
    echo "✓ Deploy concluído com sucesso!"
else
    echo "✗ Erro no deploy!"
    exit 1
fi
echo ""

# 3. Criar/Atualizar job de migração
echo "▶ Configurando job de migração..."
echo ""

if gcloud run jobs describe migrate-monpec-complete --region="$REGION" &>/dev/null; then
    echo "   Job já existe. Atualizando..."
    gcloud run jobs update migrate-monpec-complete \
        --image "${IMAGE_NAME}:latest" \
        --region="$REGION" \
        --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=${CONNECTION_NAME},DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=${DB_PASSWORD}" \
        --set-cloudsql-instances="$CONNECTION_NAME" \
        --memory=2Gi \
        --cpu=1 \
        --max-retries=3 \
        --task-timeout=600 \
        --quiet
else
    echo "   Criando novo job..."
    gcloud run jobs create migrate-monpec-complete \
        --image "${IMAGE_NAME}:latest" \
        --region="$REGION" \
        --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,CLOUD_SQL_CONNECTION_NAME=${CONNECTION_NAME},DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=${DB_PASSWORD}" \
        --set-cloudsql-instances="$CONNECTION_NAME" \
        --command="python" \
        --args="manage.py,migrate,--noinput" \
        --memory=2Gi \
        --cpu=1 \
        --max-retries=3 \
        --task-timeout=600 \
        --quiet
fi

echo "✓ Job configurado"
echo ""

# 4. Executar migrações
echo "▶ Executando migrações..."
echo "   Isso pode levar alguns minutos..."
echo ""

gcloud run jobs execute migrate-monpec-complete --region="$REGION" --wait

if [ $? -eq 0 ]; then
    echo "✓ Migrações aplicadas com sucesso!"
else
    echo "⚠ Migrações podem ter falhado. Verifique os logs:"
    echo "   gcloud run jobs executions list --job=migrate-monpec-complete --region=$REGION"
fi
echo ""

# 5. Obter URL
echo "▶ Verificando URL do serviço..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo "✓ Serviço disponível em: $SERVICE_URL"
    echo ""
    echo "   Testando conexão..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✓ Serviço está funcionando! (HTTP 200)"
    else
        echo "⚠ Serviço retornou HTTP $HTTP_CODE"
    fi
else
    echo "⚠ Não foi possível obter a URL do serviço"
fi
echo ""

# Resumo final
echo "========================================"
echo "✅ BUILD E DEPLOY CONCLUÍDOS!"
echo "========================================"
echo ""
echo "📋 Resumo:"
echo "  • Imagem: ${IMAGE_NAME}:latest"
echo "  • Serviço: $SERVICE_NAME"
echo "  • Região: $REGION"
[ -n "$SERVICE_URL" ] && echo "  • URL: $SERVICE_URL"
echo ""
echo "🔗 Próximos passos:"
[ -n "$SERVICE_URL" ] && echo "  1. Acesse o sistema: $SERVICE_URL"
echo "  2. Verifique os logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo "  3. Teste o cadastro de novo produtor com o campo 'Vai emitir NF-e'"
echo ""
