#!/bin/bash
# Script Final de Deploy para Google Cloud Run
# Execute este script no Google Cloud Shell

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "========================================"
echo "🚀 DEPLOY FINAL - MONPEC PARA GCP"
echo "========================================"
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
CONNECTION_NAME="monpec-sistema-rural:us-central1:monpec-db"
SECRET_KEY="rfzjy1t-wda0oi+p!_4!4-n-1a60"
DB_PASSWORD="L6171r12@@jjms"

# 1. Configurar projeto
echo -e "${BLUE}📋${NC} Configurando projeto GCP..."
gcloud config set project "$PROJECT_ID" --quiet
echo -e "${GREEN}✅${NC} Projeto configurado: $PROJECT_ID"
echo ""

# 2. Build da imagem
echo -e "${BLUE}🏗️${NC} Fazendo build da imagem Docker..."
echo "   Isso pode levar 5-10 minutos..."
echo ""

if gcloud builds submit . --tag "${IMAGE_NAME}:latest" --timeout=20m; then
    echo -e "${GREEN}✅${NC} Build concluído com sucesso!"
else
    echo -e "${RED}❌${NC} Erro no build da imagem!"
    echo -e "${YELLOW}💡${NC} Verifique os logs com: gcloud builds list"
    exit 1
fi
echo ""

# 3. Deploy no Cloud Run
echo -e "${BLUE}🚀${NC} Fazendo deploy no Cloud Run..."
echo ""

gcloud run deploy "$SERVICE_NAME" \
    --image "${IMAGE_NAME}:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
    --set-env-vars "DEBUG=False" \
    --set-env-vars "SECRET_KEY=$SECRET_KEY" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars "DB_NAME=monpec_db" \
    --set-env-vars "DB_USER=monpec_user" \
    --set-env-vars "DB_PASSWORD=$DB_PASSWORD" \
    --set-env-vars "DB_HOST=34.9.51.178" \
    --set-env-vars "DB_PORT=5432" \
    --set-env-vars "CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME" \
    --set-env-vars "SITE_URL=https://monpec.com.br" \
    --add-cloudsql-instances="$CONNECTION_NAME" \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80 \
    --port 8080 \
    --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅${NC} Deploy concluído com sucesso!"
else
    echo -e "${RED}❌${NC} Erro no deploy!"
    echo -e "${YELLOW}💡${NC} Verifique os logs com: gcloud run services logs read $SERVICE_NAME --region=$REGION"
    exit 1
fi
echo ""

# 4. Obter URL do serviço
echo -e "${BLUE}🔗${NC} Verificando URL do serviço..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}✅${NC} Serviço disponível em: $SERVICE_URL"
    echo ""
    echo -e "${BLUE}🧪${NC} Testando conectividade..."
    if curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" | grep -q "200\|302"; then
        echo -e "${GREEN}✅${NC} Serviço está respondendo! (HTTP 200/302)"
    else
        echo -e "${YELLOW}⚠️${NC} Serviço pode estar inicializando..."
    fi
else
    echo -e "${YELLOW}⚠️${NC} Não foi possível obter a URL do serviço"
fi
echo ""

# 5. Instruções finais
echo "========================================"
echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo "========================================"
echo ""
echo "📋 Resumo da configuração:"
echo "  • Projeto: $PROJECT_ID"
echo "  • Serviço: $SERVICE_NAME"
echo "  • Região: $REGION"
echo "  • Memória: 2GB"
echo "  • CPU: 2 vCPUs"
echo "  • Instâncias máx: 10"
echo "  • Timeout: 300s"
[ -n "$SERVICE_URL" ] && echo "  • URL: $SERVICE_URL"
echo ""
echo "🔧 Próximos passos:"
echo "  1. Acesse: $SERVICE_URL"
echo "  2. Verifique se não há erros 500"
echo "  3. Teste o cadastro de usuários"
echo "  4. Configure o domínio personalizado se necessário"
echo ""
echo "📊 Comandos úteis:"
echo "  • Logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
echo "  • Status: gcloud run services describe $SERVICE_NAME --region=$REGION"
echo "  • Reiniciar: gcloud run services update $SERVICE_NAME --region=$REGION --no-traffic"
echo ""