#!/bin/bash
# Script Completo de Build e Deploy - Google Cloud Run
# Execute este script no Google Cloud Shell

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "========================================"
echo "  BUILD E DEPLOY COMPLETO - MONPEC"
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
echo -e "${BLUE}▶${NC} Configurando projeto..."
gcloud config set project "$PROJECT_ID" --quiet
echo -e "${GREEN}✓${NC} Projeto configurado"
echo ""

# 1. Build da imagem
echo -e "${BLUE}▶${NC} Fazendo build da imagem Docker..."
echo "   Isso pode levar 5-10 minutos..."
echo ""

if gcloud builds submit . --tag "${IMAGE_NAME}:latest" --timeout=20m; then
    echo -e "${GREEN}✓${NC} Build concluído com sucesso!"
else
    echo -e "${RED}✗${NC} Erro no build da imagem!"
    exit 1
fi
echo ""

# 2. Deploy no Cloud Run
echo -e "${BLUE}▶${NC} Fazendo deploy no Cloud Run..."
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
    echo -e "${GREEN}✓${NC} Deploy concluído com sucesso!"
else
    echo -e "${RED}✗${NC} Erro no deploy!"
    exit 1
fi
echo ""

# 3. Criar/Atualizar job de migração
echo -e "${BLUE}▶${NC} Configurando job de migração..."
echo ""

# Verificar se job já existe
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

echo -e "${GREEN}✓${NC} Job configurado"
echo ""

# 4. Executar migrações
echo -e "${BLUE}▶${NC} Executando migrações..."
echo "   Isso pode levar alguns minutos..."
echo ""

if gcloud run jobs execute migrate-monpec-complete --region="$REGION" --wait; then
    echo -e "${GREEN}✓${NC} Migrações aplicadas com sucesso!"
else
    echo -e "${YELLOW}⚠${NC} Migrações podem ter falhado. Verifique os logs:"
    echo "   gcloud run jobs executions list --job=migrate-monpec-complete --region=$REGION"
fi
echo ""

# 5. Obter URL e testar
echo -e "${BLUE}▶${NC} Verificando URL do serviço..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}✓${NC} Serviço disponível em: $SERVICE_URL"
    echo ""
    echo "   Testando conexão..."
    if curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" | grep -q "200"; then
        echo -e "${GREEN}✓${NC} Serviço está funcionando! (HTTP 200)"
    else
        echo -e "${YELLOW}⚠${NC} Serviço pode estar com problemas"
    fi
else
    echo -e "${YELLOW}⚠${NC} Não foi possível obter a URL do serviço"
fi
echo ""

# Resumo final
echo "========================================"
echo -e "${GREEN}✅ BUILD E DEPLOY CONCLUÍDOS!${NC}"
echo "========================================"
echo ""
echo "📋 Resumo:"
echo "  • Imagem: ${IMAGE_NAME}:latest"
echo "  • Serviço: $SERVICE_NAME"
echo "  • Região: $REGION"
[ -n "$SERVICE_URL" ] && echo "  • URL: $SERVICE_URL"
echo ""
echo "🔗 Próximos passos:"
echo "  1. Acesse o sistema: $SERVICE_URL"
echo "  2. Verifique os logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo "  3. Teste o cadastro de novo produtor com o campo 'Vai emitir NF-e'"
echo ""
