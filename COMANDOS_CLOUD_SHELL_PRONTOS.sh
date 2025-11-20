#!/bin/bash
# Script com comandos prontos para copiar e colar no Cloud Shell
# Execute um comando por vez ou todo o script

echo "🚀 MONPEC - Deploy no Google Cloud"
echo "=================================="
echo ""

# PASSO 1: Verificar autenticação
echo "📋 PASSO 1: Verificando autenticação..."
gcloud auth list

# PASSO 2: Criar/Configurar projeto
echo ""
echo "📋 PASSO 2: Configurando projeto..."
gcloud projects create monpec-sistema-rural --name="MONPEC Sistema Rural" 2>/dev/null || echo "Projeto já existe ou erro ao criar"
gcloud config set project monpec-sistema-rural

# Verificar projeto
echo "✅ Projeto configurado:"
gcloud config get-value project

# PASSO 3: Habilitar APIs
echo ""
echo "📋 PASSO 3: Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo "✅ APIs habilitadas!"

# PASSO 4: Criar banco de dados
echo ""
echo "📋 PASSO 4: Criando banco de dados Cloud SQL..."
echo "⏳ Isso pode levar 5-10 minutos..."

# Verificar se já existe
if gcloud sql instances describe monpec-db &>/dev/null; then
    echo "⚠️  Instância já existe. Pulando criação..."
else
    gcloud sql instances create monpec-db \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=us-central1 \
        --root-password=Monpec2025!
    
    echo "⏳ Aguardando instância ficar pronta..."
    sleep 30
    
    # Criar banco
    gcloud sql databases create monpec_db --instance=monpec-db
    
    # Criar usuário
    gcloud sql users create monpec_user \
        --instance=monpec-db \
        --password=Monpec2025!
fi

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
echo "✅ Connection Name: $CONNECTION_NAME"
echo "⚠️  ANOTE ESSE VALOR: $CONNECTION_NAME"

echo ""
echo "✅ Configuração inicial concluída!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Faça upload do código (pasta Monpec_projetista) via File Explorer"
echo "2. Execute: cd Monpec_projetista"
echo "3. Execute: gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec"
echo ""






