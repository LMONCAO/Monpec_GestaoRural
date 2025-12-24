#!/bin/bash
# Script para diagnosticar por que a migração falhou

JOB_NAME="migrate-monpec"
REGION="us-central1"  # ✅ CORRIGIDO

echo "========================================"
echo "🔍 Diagnosticando Falha na Migração"
echo "========================================"
echo ""

# 1. Verificar última execução
echo "1️⃣  Verificando última execução do job..."
LAST_EXEC=$(gcloud run jobs executions list --job $JOB_NAME --region $REGION --limit 1 --format="value(name)" 2>/dev/null | head -1)

if [ -n "$LAST_EXEC" ]; then
    echo "✅ Última execução encontrada: $LAST_EXEC"
    echo ""
    echo "Detalhes da execução:"
    gcloud run jobs executions describe $LAST_EXEC --region $REGION 2>/dev/null | grep -E "name|status|message|error" || echo "Erro ao obter detalhes"
    echo ""
    
    echo "Logs da execução:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME" --limit 20 --format="table(timestamp,severity,textPayload)" 2>/dev/null | head -30
else
    echo "⚠️  Nenhuma execução encontrada"
fi
echo ""

# 2. Verificar variáveis de ambiente do job
echo "2️⃣  Verificando variáveis de ambiente do job..."
gcloud run jobs describe $JOB_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null
echo ""

# 3. Verificar se o serviço principal tem variáveis configuradas
echo "3️⃣  Verificando variáveis do serviço principal..."
SERVICE_ENV=$(gcloud run services describe monpec --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null)
if [ -n "$SERVICE_ENV" ]; then
    echo "Variáveis do serviço:"
    echo "$SERVICE_ENV" | tr ',' '\n' | head -10
    echo ""
    
    if echo "$SERVICE_ENV" | grep -q "DB_HOST"; then
        echo "✅ DB_HOST está configurado no serviço"
    else
        echo "⚠️  DB_HOST NÃO está configurado no serviço"
    fi
else
    echo "⚠️  Nenhuma variável de ambiente encontrada no serviço"
fi
echo ""

# 4. Verificar conectividade com banco de dados
echo "4️⃣  Verificando configuração do banco de dados..."
echo "⚠️  Para verificar conectividade, você precisa:"
echo "   1. Configurar as variáveis de ambiente no job"
echo "   2. Ou executar o job com as mesmas variáveis do serviço"
echo ""

echo "========================================"
echo "💡 SOLUÇÃO:"
echo "========================================"
echo ""
echo "O job de migração precisa das variáveis de ambiente do banco de dados."
echo ""
echo "Opção 1: Atualizar o job com as variáveis:"
echo "  gcloud run jobs update $JOB_NAME --region $REGION \\"
echo "    --update-env-vars 'DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME'"
echo ""
echo "Opção 2: Executar migrações diretamente no serviço (recomendado):"
echo "  gcloud run services update monpec --region $REGION \\"
echo "    --update-env-vars 'DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME'"
echo ""
echo "  Depois execute:"
echo "  gcloud run jobs execute $JOB_NAME --region $REGION --wait"
echo ""



