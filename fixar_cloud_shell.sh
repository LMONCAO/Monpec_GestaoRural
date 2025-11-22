#!/bin/bash
# Script para corrigir problemas no Cloud Shell e fazer deploy

echo "========================================"
echo "  CORRIGINDO CLOUD SHELL E FAZENDO DEPLOY"
echo "========================================"
echo ""

# 1. Configurar Git (AJUSTE OS VALORES ABAIXO!)
echo "📝 Configurando Git..."
echo "⚠️  IMPORTANTE: Ajuste o email e nome abaixo!"
echo ""
read -p "Digite seu email do GitHub: " GIT_EMAIL
read -p "Digite seu nome: " GIT_NAME

git config --global user.email "$GIT_EMAIL"
git config --global user.name "$GIT_NAME"

echo "✅ Git configurado!"
echo ""

# 2. Ir para a pasta do projeto
echo "📁 Navegando para a pasta do projeto..."
if [ -d "Monpec_GestaoRural" ]; then
    cd Monpec_GestaoRural
else
    echo "❌ Pasta Monpec_GestaoRural não encontrada!"
    echo "   Execute: git clone https://github.com/LMONCAO/Monpec_GestaoRural.git"
    exit 1
fi

# 3. Atualizar código do GitHub
echo "📥 Atualizando código do GitHub..."
git pull origin master || git pull origin main

# 4. Dar permissão ao script
echo "🔧 Configurando permissões..."
if [ -f "deploy_completo_cloud_shell.sh" ]; then
    chmod +x deploy_completo_cloud_shell.sh
    echo "✅ Script de deploy configurado!"
else
    echo "⚠️  Script deploy_completo_cloud_shell.sh não encontrado!"
    echo "   Vou fazer deploy manualmente..."
    
    # Deploy manual
    echo ""
    echo "🔨 Fazendo build..."
    gcloud config set project monpec-sistema-rural
    gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
    
    echo ""
    echo "🚀 Fazendo deploy..."
    gcloud run deploy monpec \
        --image gcr.io/monpec-sistema-rural/monpec \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated \
        --add-cloudsql-instances monpec-sistema-rural:us-central1:monpec-db \
        --set-env-vars \
            DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,\
            DEBUG=False,\
            DB_NAME=monpec_db,\
            DB_USER=monpec_user,\
            DB_PASSWORD="Monpec2025!",\
            CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,\
            SECRET_KEY="$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" \
        --memory=512Mi \
        --cpu=1 \
        --timeout=300 \
        --max-instances=10
    
    exit 0
fi

# 5. Executar deploy
echo ""
echo "🚀 Executando deploy..."
echo "⏳ Isso pode levar 15-20 minutos..."
echo ""
./deploy_completo_cloud_shell.sh

echo ""
echo "========================================"
echo "  ✅ CONCLUÍDO!"
echo "========================================"

