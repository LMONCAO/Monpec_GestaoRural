#!/bin/bash
# Script para configurar TODAS as variáveis de ambiente necessárias

SERVICE_NAME="monpec"
REGION="us-central1"

echo "========================================"
echo "⚙️  Configuração de Variáveis de Ambiente"
echo "========================================"
echo ""

# Valores padrão (produção Mercado Pago)
MP_ACCESS_TOKEN="APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940"
MP_PUBLIC_KEY="APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3"

echo "Usando credenciais de produção do Mercado Pago..."
echo ""

# Solicitar informações do banco de dados
read -p "DB_NAME [monpec_db]: " DB_NAME
DB_NAME=${DB_NAME:-monpec_db}

read -p "DB_USER [monpec_user]: " DB_USER
DB_USER=${DB_USER:-monpec_user}

read -sp "DB_PASSWORD: " DB_PASSWORD
echo ""

read -p "DB_HOST (ex: /cloudsql/PROJECT:REGION:INSTANCE ou IP): " DB_HOST

read -sp "SECRET_KEY (ou pressione Enter para gerar automaticamente): " SECRET_KEY
echo ""

# Gerar SECRET_KEY se não fornecida
if [ -z "$SECRET_KEY" ]; then
    echo "Gerando SECRET_KEY..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    echo "✅ SECRET_KEY gerada"
fi

echo ""
echo "Atualizando variáveis de ambiente no Cloud Run..."
echo ""

gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars "MERCADOPAGO_ACCESS_TOKEN=$MP_ACCESS_TOKEN,MERCADOPAGO_PUBLIC_KEY=$MP_PUBLIC_KEY,SECRET_KEY=$SECRET_KEY,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DB_HOST=$DB_HOST"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Variáveis de ambiente configuradas com sucesso!"
    echo ""
    echo "📝 Variáveis configuradas:"
    echo "  - MERCADOPAGO_ACCESS_TOKEN: ✅"
    echo "  - MERCADOPAGO_PUBLIC_KEY: ✅"
    echo "  - SECRET_KEY: ✅"
    echo "  - DB_NAME: $DB_NAME"
    echo "  - DB_USER: $DB_USER"
    echo "  - DB_PASSWORD: ✅ (configurada)"
    echo "  - DB_HOST: $DB_HOST"
else
    echo ""
    echo "❌ Erro ao configurar variáveis de ambiente"
    exit 1
fi

echo ""





















