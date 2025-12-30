#!/bin/bash
# Script para DIAGNOSTICAR o erro real e CORRIGIR
# Execute no Cloud Shell

set -e

echo "========================================"
echo "  DIAGNOSTICANDO E CORRIGINDO ERRO"
echo "========================================"
echo ""

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

# 1. Verificar logs do serviço
echo "1. Verificando logs do serviço (últimas 50 linhas)..."
echo "----------------------------------------"
gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50
echo "----------------------------------------"
echo ""

# 2. Verificar status do serviço
echo "2. Verificando status do serviço..."
gcloud run services describe $SERVICE_NAME --region $REGION --format="yaml(status)" | head -20
echo ""

# 3. Verificar variáveis de ambiente
echo "3. Verificando variáveis de ambiente..."
gcloud run services describe $SERVICE_NAME --region $REGION --format="yaml(spec.template.spec.containers[0].env)" | grep -E "(name|value)" | head -20
echo ""

# 4. Verificar se o banco de dados está acessível
echo "4. Verificando conexão com Cloud SQL..."
gcloud sql instances describe monpec-db --format="yaml(state,settings.databaseFlags)" | head -10
echo ""

# 5. Testar acesso HTTP
echo "5. Testando acesso HTTP..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    echo "URL: $SERVICE_URL"
    echo "Testando..."
    HTTP_CODE=$(curl -s -o /tmp/response.html -w "%{http_code}" --max-time 10 "$SERVICE_URL" 2>/dev/null || echo "000")
    echo "Código HTTP: $HTTP_CODE"
    if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "000" ]; then
        echo "Resposta (primeiras 500 caracteres):"
        head -c 500 /tmp/response.html 2>/dev/null || echo "Não foi possível obter resposta"
    fi
else
    echo "URL não disponível"
fi
echo ""

echo "========================================"
echo "  ANÁLISE CONCLUÍDA"
echo "========================================"
echo ""
echo "Procure por erros nos logs acima e me informe qual erro apareceu."
















