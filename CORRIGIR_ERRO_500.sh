#!/bin/bash
# Script para CORRIGIR o erro 500 Internal Server Error
# Baseado nos problemas mais comuns

set -e

echo "========================================"
echo "  CORRIGINDO ERRO 500"
echo "========================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Verificar logs primeiro
echo "1. Verificando logs para identificar o erro..."
echo "----------------------------------------"
LOGS=$(gcloud run services logs read $SERVICE_NAME --region $REGION --limit=100 2>&1)
echo "$LOGS" | tail -30
echo "----------------------------------------"
echo ""

# Verificar se há erro de SECRET_KEY
if echo "$LOGS" | grep -qi "SECRET_KEY"; then
    echo "⚠️  Erro relacionado a SECRET_KEY detectado"
    echo "Corrigindo..."
fi

# Verificar se há erro de banco de dados
if echo "$LOGS" | grep -qi "database\|postgres\|connection"; then
    echo "⚠️  Erro relacionado a banco de dados detectado"
    echo "Verificando conexão..."
fi

# Verificar se há erro de importação
if echo "$LOGS" | grep -qi "ImportError\|ModuleNotFoundError"; then
    echo "⚠️  Erro de módulo não encontrado detectado"
    echo "Verificando requirements.txt..."
fi

# Atualizar variáveis de ambiente com valores corretos
echo ""
echo "2. Atualizando variáveis de ambiente..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"
ENV_VARS="${ENV_VARS},DEBUG=False"
ENV_VARS="${ENV_VARS},SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t"
ENV_VARS="${ENV_VARS},DB_NAME=monpec_db"
ENV_VARS="${ENV_VARS},DB_USER=monpec_user"
ENV_VARS="${ENV_VARS},DB_PASSWORD=Django2025@"
ENV_VARS="${ENV_VARS},CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db"
ENV_VARS="${ENV_VARS},PYTHONUNBUFFERED=1"

gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars "$ENV_VARS"

echo "✅ Variáveis de ambiente atualizadas"
echo ""

# Verificar se precisa aplicar migrações
echo "3. Verificando se precisa aplicar migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait 2>&1 | tail -10
echo ""

# Obter URL e testar
echo "4. Obtendo URL e testando..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
echo "URL: $SERVICE_URL"
echo ""
echo "Aguarde 30 segundos e teste novamente no navegador..."
echo ""

echo "========================================"
echo "  CORREÇÕES APLICADAS"
echo "========================================"
echo ""
echo "Se ainda houver erro, execute:"
echo "  gcloud run services logs read $SERVICE_NAME --region $REGION --limit=100"
echo ""









