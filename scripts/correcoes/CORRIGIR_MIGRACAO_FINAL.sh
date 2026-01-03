#!/bin/bash
# Script para corrigir a migração que está falhando

JOB_NAME="migrate-monpec"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "========================================"
echo "🔧 Corrigindo Migração Falhada"
echo "========================================"
echo ""

# 1. Ver detalhes do erro
echo "1️⃣  Verificando detalhes do erro..."
LAST_EXEC=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --limit 1 --format="value(name)" 2>/dev/null | head -1)
if [ -n "$LAST_EXEC" ]; then
    echo "Última execução: $LAST_EXEC"
    echo ""
    echo "Detalhes:"
    gcloud run jobs executions describe $LAST_EXEC --region $REGION 2>/dev/null | grep -A 10 "status\|message\|error" || echo "Verifique no console"
fi
echo ""

# 2. Ver variáveis do serviço
echo "2️⃣  Obtendo variáveis de ambiente do serviço..."
SERVICE_ENV=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null)

if [ -z "$SERVICE_ENV" ]; then
    echo "❌ Não foi possível obter variáveis do serviço"
    echo ""
    echo "Configure manualmente as variáveis do banco de dados:"
    echo ""
    echo "gcloud run jobs update $JOB_NAME --region $REGION \\"
    echo "  --update-env-vars 'DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'"
    exit 1
fi

echo "Variáveis encontradas no serviço:"
echo "$SERVICE_ENV" | tr ',' '\n' | head -10
echo ""

# 3. Verificar se tem variáveis de banco
if ! echo "$SERVICE_ENV" | grep -q "DB_HOST"; then
    echo "⚠️  ATENÇÃO: O serviço não tem variáveis de banco de dados configuradas!"
    echo ""
    echo "Configure primeiro no serviço:"
    echo ""
    echo "gcloud run services update $SERVICE_NAME --region $REGION \\"
    echo "  --update-env-vars 'DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME'"
    echo ""
    exit 1
fi

# 4. Atualizar job com variáveis do serviço
echo "3️⃣  Atualizando job com variáveis do serviço..."
gcloud run jobs update $JOB_NAME --region $REGION --update-env-vars "$SERVICE_ENV"

if [ $? -eq 0 ]; then
    echo "✅ Job atualizado com sucesso!"
else
    echo "❌ Erro ao atualizar job"
    exit 1
fi
echo ""

# 5. Executar migração novamente
echo "4️⃣  Executando migração novamente..."
echo "Aguarde, isso pode levar alguns minutos..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ Migração executada com sucesso!"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "❌ Migração ainda falhou"
    echo "========================================"
    echo ""
    echo "Verifique os logs detalhados:"
    echo "  gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --limit 50 --format=\"table(timestamp,severity,textPayload)\""
    echo ""
fi




























