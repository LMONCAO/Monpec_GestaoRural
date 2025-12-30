#!/bin/bash
# Script de deploy profissional para Google Cloud Run
# Sistema: MonPEC - Monitor de Plano Orçamentário

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DEPLOY MONPEC - GOOGLE CLOUD RUN${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERRO: gcloud CLI não está instalado!${NC}"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Obter projeto atual
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}Nenhum projeto configurado.${NC}"
    echo "Listando projetos disponíveis..."
    gcloud projects list
    echo ""
    read -p "Digite o PROJECT_ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

echo -e "${GREEN}Projeto: ${PROJECT_ID}${NC}"
echo ""

# Confirmar deploy
read -p "Deseja continuar com o deploy? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Deploy cancelado."
    exit 0
fi

# Habilitar APIs necessárias
echo -e "${YELLOW}Habilitando APIs necessárias...${NC}"
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable cloudresourcemanager.googleapis.com --quiet
echo -e "${GREEN}APIs habilitadas!${NC}"
echo ""

# Verificar se Cloud SQL existe
echo -e "${YELLOW}Verificando configuração do banco de dados...${NC}"
DB_INSTANCE=$(gcloud sql instances list --format="value(name)" --filter="name:monpec*" 2>/dev/null | head -n 1)

if [ -z "$DB_INSTANCE" ]; then
    echo -e "${YELLOW}Nenhuma instância Cloud SQL encontrada.${NC}"
    echo "Você precisa criar uma instância Cloud SQL PostgreSQL primeiro."
    echo ""
    echo "Execute:"
    echo "  gcloud sql instances create monpec-db \\"
    echo "    --database-version=POSTGRES_15 \\"
    echo "    --tier=db-f1-micro \\"
    echo "    --region=us-central1 \\"
    echo "    --root-password=SUA_SENHA_AQUI"
    echo ""
    read -p "Deseja criar agora? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        read -sp "Digite a senha do root do PostgreSQL: " DB_ROOT_PASSWORD
        echo
        gcloud sql instances create monpec-db \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=us-central1 \
            --root-password=$DB_ROOT_PASSWORD
        DB_INSTANCE="monpec-db"
        echo -e "${GREEN}Instância criada!${NC}"
    else
        echo "Continuando sem banco de dados..."
    fi
else
    echo -e "${GREEN}Instância encontrada: ${DB_INSTANCE}${NC}"
fi
echo ""

# Iniciar build e deploy
echo -e "${YELLOW}Iniciando build e deploy...${NC}"
echo "Isso pode levar alguns minutos..."
echo ""

gcloud builds submit --config cloudbuild.yaml

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe monpec --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "")

if [ ! -z "$SERVICE_URL" ]; then
    echo -e "${GREEN}URL do serviço: ${SERVICE_URL}${NC}"
    echo ""
fi

echo -e "${YELLOW}Próximos passos:${NC}"
echo ""
echo "1. Configure as variáveis de ambiente no Cloud Run:"
echo "   gcloud run services update monpec \\"
echo "     --region=us-central1 \\"
echo "     --set-env-vars=\"SECRET_KEY=SUA_SECRET_KEY_AQUI\" \\"
echo "     --set-env-vars=\"DB_NAME=monpec_db\" \\"
echo "     --set-env-vars=\"DB_USER=monpec_user\" \\"
echo "     --set-env-vars=\"DB_PASSWORD=SUA_SENHA_AQUI\" \\"
echo "     --set-env-vars=\"CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME\" \\"
echo "     --set-env-vars=\"MERCADOPAGO_ACCESS_TOKEN=SEU_TOKEN_AQUI\" \\"
echo "     --set-env-vars=\"MERCADOPAGO_PUBLIC_KEY=SUA_PUBLIC_KEY_AQUI\""
echo ""
echo "2. Aplique as migrações do banco de dados:"
echo "   gcloud run jobs create migrate-monpec \\"
echo "     --image=gcr.io/${PROJECT_ID}/monpec:latest \\"
echo "     --region=us-central1 \\"
echo "     --command=python \\"
echo "     --args=manage.py,migrate \\"
echo "     --set-env-vars=\"DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp\" \\"
echo "     --set-env-vars=\"CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME\" \\"
echo "     --set-env-vars=\"DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA\""
echo ""
echo "   gcloud run jobs execute migrate-monpec --region=us-central1"
echo ""
echo "3. Crie um superusuário:"
echo "   gcloud run jobs create create-superuser \\"
echo "     --image=gcr.io/${PROJECT_ID}/monpec:latest \\"
echo "     --region=us-central1 \\"
echo "     --command=python \\"
echo "     --args=manage.py,createsuperuser \\"
echo "     --set-env-vars=\"DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp\""
echo ""
echo "4. Configure domínio personalizado (opcional):"
echo "   gcloud run domain-mappings create \\"
echo "     --service=monpec \\"
echo "     --domain=monpec.com.br \\"
echo "     --region=us-central1"
echo ""
echo "5. Acesse o console:"
echo "   https://console.cloud.google.com/run/detail/us-central1/monpec"
echo ""
