#!/bin/bash
# Script para continuar o deploy após gcloud init

echo "🚀 Continuando deploy do MONPEC..."
echo ""

# Verificar se o projeto está configurado
PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT" ]; then
    echo "❌ Nenhum projeto configurado. Execute: gcloud config set project monpec-sistema-rural"
    exit 1
fi

echo "✅ Projeto: $PROJECT"
echo ""

# Habilitar APIs
echo "📡 Habilitando APIs necessárias..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com \
    containerregistry.googleapis.com

echo "✅ APIs habilitadas!"
echo ""

# Verificar se o banco já existe
echo "🗄️  Verificando banco de dados..."
if gcloud sql instances describe monpec-db &>/dev/null; then
    echo "✅ Instância monpec-db já existe"
    CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
    echo "   Connection Name: $CONNECTION_NAME"
else
    echo "⏳ Criando instância PostgreSQL (pode levar 5-10 minutos)..."
    gcloud sql instances create monpec-db \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=us-central1 \
        --root-password=Monpec2025!
    
    echo "📊 Criando banco de dados..."
    gcloud sql databases create monpec_db --instance=monpec-db
    
    echo "👤 Criando usuário..."
    gcloud sql users create monpec_user \
        --instance=monpec-db \
        --password=Monpec2025!
    
    CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
    echo "✅ Connection Name: $CONNECTION_NAME"
fi

echo ""
echo "📋 Próximos passos:"
echo "1. Faça upload do código para o Cloud Shell (se ainda não fez)"
echo "2. Execute: cd Monpec_projetista"
echo "3. Execute: gcloud builds submit --tag gcr.io/$PROJECT/monpec"
echo ""
echo "Ou continue com o arquivo COMECE_AGORA.md a partir do Passo 5"
echo ""







