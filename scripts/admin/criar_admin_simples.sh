#!/bin/bash
# Script para criar admin via Cloud Run Job
# Execute: bash criar_admin_simples.sh

set -e

echo "🔐 Criando Admin via Cloud Run Job"
echo ""

# Obter connection name
echo "▶ Obtendo informações do Cloud SQL..."
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)" 2>/dev/null || echo "")
if [ -z "$CONNECTION_NAME" ]; then
    echo "❌ Erro: Não foi possível obter connection name"
    echo "   Certifique-se de que a instância 'monpec-db' existe"
    exit 1
fi

echo "✅ Connection Name: $CONNECTION_NAME"
echo ""

# Pedir senha do banco
echo "⚠️  Digite a senha do banco de dados (ou pressione Enter para usar padrão):"
read -s DB_PASSWORD
if [ -z "$DB_PASSWORD" ]; then
    DB_PASSWORD="Monpec2025!SenhaSegura"
    echo "   Usando senha padrão"
fi

echo ""
echo "▶ Criando Cloud Run Job..."
gcloud run jobs create create-admin \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --command python \
  --args criar_admin_producao.py \
  --set-env-vars DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1 \
  2>&1 | grep -v "Job.*already exists" || true

echo ""
echo "▶ Executando job (isso pode levar 1-2 minutos)..."
gcloud run jobs execute create-admin --region us-central1 --wait

echo ""
echo "✅ Concluído!"
echo ""
echo "🔐 Credenciais:"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"
echo ""
echo "🌐 Teste em: https://monpec-29862706245.us-central1.run.app/login/"
echo ""

