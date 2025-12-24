#!/bin/bash
# Script simples para executar migração com variáveis configuradas manualmente

JOB_NAME="migrate-monpec"
REGION="us-central1"  # ✅ CORRIGIDO

echo "========================================"
echo "🗄️  Executar Migração - Versão Simples"
echo "========================================"
echo ""
echo "Este script atualizará o job com as variáveis e executará a migração."
echo ""

# Solicitar variáveis
read -p "DB_NAME [monpec_db]: " DB_NAME
DB_NAME=${DB_NAME:-monpec_db}

read -p "DB_USER [monpec_user]: " DB_USER
DB_USER=${DB_USER:-monpec_user}

read -sp "DB_PASSWORD: " DB_PASSWORD
echo ""

read -p "DB_HOST (ex: /cloudsql/PROJECT:REGION:INSTANCE): " DB_HOST

read -sp "SECRET_KEY (ou Enter para pular): " SECRET_KEY
echo ""

# Montar variáveis de ambiente
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DB_HOST=$DB_HOST"

if [ -n "$SECRET_KEY" ]; then
    ENV_VARS="$ENV_VARS,SECRET_KEY=$SECRET_KEY"
fi

echo ""
echo "Atualizando job com variáveis de ambiente..."
gcloud run jobs update $JOB_NAME --region $REGION --update-env-vars "$ENV_VARS"

if [ $? -ne 0 ]; then
    echo "❌ Erro ao atualizar job"
    exit 1
fi

echo "✅ Job atualizado"
echo ""
echo "Executando migração (isso pode levar alguns minutos)..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ Migração concluída com sucesso!"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "❌ Migração falhou"
    echo "========================================"
    echo ""
    echo "Verifique os logs para mais detalhes:"
    echo "  gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --limit 50 --format=\"table(timestamp,severity,textPayload)\""
    echo ""
fi


