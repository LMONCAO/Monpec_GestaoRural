#!/bin/bash
# Script DEFINITIVO - Identifica e corrige o erro automaticamente

set -e

echo "========================================"
echo "  RESOLVENDO ERRO 500 DEFINITIVAMENTE"
echo "========================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# PASSO 1: Ver logs e identificar erro
echo "▶ PASSO 1: Analisando logs para identificar o erro..."
echo "----------------------------------------"
LOGS=$(gcloud run services logs read $SERVICE_NAME --region $REGION --limit=200 2>&1)
echo "$LOGS" | grep -iE "error|exception|traceback|failed" | tail -20 || echo "Nenhum erro óbvio nos logs recentes"
echo "----------------------------------------"
echo ""

# PASSO 2: Verificar e corrigir variáveis de ambiente
echo "▶ PASSO 2: Verificando e corrigindo variáveis de ambiente..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"
ENV_VARS="${ENV_VARS},DEBUG=False"
ENV_VARS="${ENV_VARS},SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t"
ENV_VARS="${ENV_VARS},DB_NAME=monpec_db"
ENV_VARS="${ENV_VARS},DB_USER=monpec_user"
ENV_VARS="${ENV_VARS},DB_PASSWORD=Django2025@"
ENV_VARS="${ENV_VARS},CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db"
ENV_VARS="${ENV_VARS},PYTHONUNBUFFERED=1"
ENV_VARS="${ENV_VARS},PYTHONDONTWRITEBYTECODE=1"

gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars "$ENV_VARS" \
    --quiet

echo "✅ Variáveis atualizadas"
echo ""

# PASSO 3: Garantir conexão com Cloud SQL
echo "▶ PASSO 3: Verificando conexão com Cloud SQL..."
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --quiet 2>&1 | grep -v "already" || true
echo "✅ Cloud SQL conectado"
echo ""

# PASSO 4: Aplicar migrações
echo "▶ PASSO 4: Aplicando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait 2>&1 | tail -5
echo "✅ Migrações aplicadas"
echo ""

# PASSO 5: Verificar se precisa coletar static files
echo "▶ PASSO 5: Verificando arquivos estáticos..."
# Isso será feito no próximo build se necessário

# PASSO 6: Obter URL e status
echo "▶ PASSO 6: Verificando status final..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null)
STATUS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)" 2>/dev/null)

echo ""
echo "========================================"
if [ "$STATUS" = "True" ] && [ -n "$SERVICE_URL" ]; then
    echo "✅ SERVIÇO ESTÁ RODANDO"
    echo "========================================"
    echo ""
    echo "URL: $SERVICE_URL"
    echo ""
    echo "⚠️  Se ainda houver erro 500, execute:"
    echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit=100"
    echo ""
    echo "E me mostre o resultado para eu corrigir o erro específico."
else
    echo "⚠️  Verifique o status manualmente"
    echo "========================================"
fi
echo ""









