#!/bin/bash
# Deploy passo a passo - evita problemas com caracteres especiais

set -e

echo "🚀 MONPEC - Deploy Passo a Passo"
echo "========================================"
echo ""

# 1. Atualizar código
echo "📥 Atualizando código..."
cd ~
if [ -d "Monpec_GestaoRural" ]; then
    cd Monpec_GestaoRural
    # Remover arquivos não rastreados que podem causar conflito
    echo "🧹 Limpando arquivos não rastreados..."
    git clean -fd
    # Fazer stash de alterações locais se houver
    git stash 2>/dev/null || true
    # Tentar pull
    git pull origin master || git pull origin main
else
    git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
    cd Monpec_GestaoRural
fi
echo "✅ Código atualizado!"
echo ""

# 2. Obter connection name
echo "🔗 Obtendo connection name..."
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)" 2>/dev/null || echo "")
if [ -z "$CONNECTION_NAME" ]; then
    echo "⚠️  Instância de banco não encontrada"
    USE_DB=false
else
    echo "✅ Connection Name: $CONNECTION_NAME"
    USE_DB=true
fi
echo ""

# 3. Gerar SECRET_KEY
echo "🔑 Gerando SECRET_KEY..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "✅ SECRET_KEY gerada"
echo ""

# 4. Build
echo "========================================"
echo "🔨 PASSO 1/2: Build da imagem"
echo "========================================"
echo "⏳ Isso pode levar 10-15 minutos..."
echo ""

gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

if [ $? -ne 0 ]; then
    echo "❌ Erro no build!"
    exit 1
fi

echo ""
echo "✅ Build concluído!"
echo ""

# 5. Deploy
echo "========================================"
echo "🚀 PASSO 2/2: Deploy no Cloud Run"
echo "========================================"
echo "⏳ Isso pode levar 2-3 minutos..."
echo ""

# Senha com ! escapada
DB_PASSWORD="Monpec2025!"

if [ "$USE_DB" = true ]; then
    gcloud run deploy monpec \
        --image gcr.io/monpec-sistema-rural/monpec \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --add-cloudsql-instances "$CONNECTION_NAME" \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
else
    gcloud run deploy monpec \
        --image gcr.io/monpec-sistema-rural/monpec \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY" \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Erro no deploy!"
    exit 1
fi

echo ""
echo "✅ Deploy concluído!"
echo ""

# 6. Obter URL
SERVICE_URL=$(gcloud run services describe monpec --region us-central1 --format 'value(status.url)')

echo "========================================"
echo "  ✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo ""
echo "🌐 URL do serviço:"
echo "   $SERVICE_URL"
echo ""

