#!/bin/bash
# Script para corrigir CLOUD_SQL_CONNECTION_NAME e adicionar Cloud SQL connection ao serviço

set -e

echo "=========================================="
echo "🔧 CORRIGINDO CLOUD SQL E ALLOWED_HOSTS"
echo "=========================================="
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
CLOUD_SQL_INSTANCE="monpec-sistema-rural:us-central1:monpec-db"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando instância do Cloud SQL..."
echo "----------------------------------------"
gcloud sql instances describe monpec-db --format="value(connectionName)" || {
    echo "❌ Instância do Cloud SQL não encontrada. Verifique se o nome está correto."
    exit 1
}

echo ""
echo "2️⃣ Adicionando conexão Cloud SQL ao serviço..."
echo "----------------------------------------"
# Adicionar Cloud SQL connection ao serviço
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --add-cloudsql-instances=$CLOUD_SQL_INSTANCE \
    --quiet

if [ $? -eq 0 ]; then
    echo "✅ Conexão Cloud SQL adicionada ao serviço"
else
    echo "⚠️ Erro ao adicionar conexão Cloud SQL (pode já estar configurada)"
fi

echo ""
echo "3️⃣ Configurando CLOUD_SQL_CONNECTION_NAME..."
echo "----------------------------------------"
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --update-env-vars "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_INSTANCE" \
    --quiet

if [ $? -eq 0 ]; then
    echo "✅ CLOUD_SQL_CONNECTION_NAME configurado: $CLOUD_SQL_INSTANCE"
else
    echo "❌ Erro ao configurar CLOUD_SQL_CONNECTION_NAME"
    exit 1
fi

echo ""
echo "4️⃣ Verificando variáveis de ambiente..."
echo "----------------------------------------"
echo "Variáveis configuradas:"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env)" | grep -E "(CLOUD_SQL_CONNECTION_NAME|SECRET_KEY|DJANGO_SETTINGS_MODULE)"

echo ""
echo "5️⃣ Verificando conexões Cloud SQL do serviço..."
echo "----------------------------------------"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)"

echo ""
echo "=========================================="
echo "✅ CORREÇÕES APLICADAS"
echo "=========================================="
echo ""
echo "📝 Próximos passos:"
echo "  1. Aguarde alguns segundos para o serviço atualizar"
echo "  2. Teste o acesso ao serviço novamente"
echo "  3. Se ainda houver erro 400, verifique os logs"
echo ""





