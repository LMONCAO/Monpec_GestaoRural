#!/bin/bash
# Script CORRIGIDO de deploy para Google Cloud Platform
# Sistema MONPEC - Execute no Google Cloud Shell

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}DEPLOY COMPLETO - MONPEC GCP${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}ERRO: manage.py não encontrado!${NC}"
    echo "Execute este script no diretório raiz do projeto."
    exit 1
fi

echo -e "${GREEN}✓ Diretório correto${NC}"
echo ""

# Obter projeto do GCP
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}⚠ Projeto GCP não configurado${NC}"
    echo "Execute: gcloud config set project SEU_PROJETO_ID"
    exit 1
fi

echo -e "${CYAN}Projeto GCP: ${PROJECT_ID}${NC}"
echo ""

# 1. Verificar autenticação
echo -e "${YELLOW}[1/7] Verificando autenticação...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠ Não autenticado. Fazendo login...${NC}"
    gcloud auth login
fi
echo -e "${GREEN}✓ Autenticado${NC}"
echo ""

# 2. Habilitar APIs necessárias
echo -e "${YELLOW}[2/7] Habilitando APIs do GCP...${NC}"
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "sqladmin.googleapis.com"
    "cloudresourcemanager.googleapis.com"
)

for api in "${APIS[@]}"; do
    gcloud services enable "$api" --quiet 2>/dev/null || true
done
echo -e "${GREEN}✓ APIs habilitadas${NC}"
echo ""

# 3. Instalar dependências locais (se necessário)
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}[3/7] Verificando dependências locais...${NC}"
    if ! python3 -c "import django" 2>/dev/null; then
        echo "Instalando dependências Python..."
        pip3 install -q -r requirements.txt 2>/dev/null || true
    fi
    echo -e "${GREEN}✓ Dependências verificadas${NC}"
else
    echo -e "${YELLOW}[3/7] requirements.txt não encontrado${NC}"
fi
echo ""

# 4. Aplicar migrações localmente (opcional, apenas para verificar)
echo -e "${YELLOW}[4/7] Verificando migrações...${NC}"
if python3 manage.py showmigrations --plan 2>/dev/null | grep -q "\[ \]"; then
    echo -e "${YELLOW}⚠ Migrações pendentes detectadas${NC}"
    echo "   (Serão aplicadas automaticamente no Cloud Run)"
else
    echo -e "${GREEN}✓ Migrações verificadas${NC}"
fi
echo ""

# 5. Configurar Dockerfile para build
echo -e "${YELLOW}[5/7] Configurando Dockerfile...${NC}"
# gcloud builds submit usa Dockerfile por padrão
# Se existe Dockerfile.prod, vamos usá-lo renomeando temporariamente
if [ -f "Dockerfile.prod" ]; then
    echo -e "${CYAN}Usando Dockerfile.prod para build${NC}"
    # Se já existe Dockerfile, fazer backup
    if [ -f "Dockerfile" ]; then
        mv Dockerfile Dockerfile.original
    fi
    # Copiar Dockerfile.prod para Dockerfile
    cp Dockerfile.prod Dockerfile
    DOCKERFILE_BACKUP=true
else
    echo -e "${GREEN}✓ Dockerfile encontrado${NC}"
    DOCKERFILE_BACKUP=false
fi
echo ""

# 6. Verificar .dockerignore
if [ ! -f ".dockerignore" ]; then
    echo -e "${YELLOW}Criando .dockerignore básico...${NC}"
    cat > .dockerignore << 'EOF'
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
*.log
.git/
.gitignore
.env
.env_local
.DS_Store
*.md
deploy/
backups/
*.ps1
*.bat
EOF
fi

# 7. Build e Deploy
echo -e "${YELLOW}[6/7] Fazendo build da imagem Docker...${NC}"
IMAGE_TAG="gcr.io/${PROJECT_ID}/monpec:latest"

# gcloud builds submit usa Dockerfile por padrão (não precisa de --file)
gcloud builds submit --tag "$IMAGE_TAG" --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build concluído${NC}"
else
    echo -e "${RED}✗ Erro no build${NC}"
    # Restaurar Dockerfile se necessário
    if [ "$DOCKERFILE_BACKUP" = true ] && [ -f "Dockerfile.original" ]; then
        mv Dockerfile.original Dockerfile
    fi
    exit 1
fi
echo ""

# Restaurar Dockerfile original se fizemos backup
if [ "$DOCKERFILE_BACKUP" = true ] && [ -f "Dockerfile.original" ]; then
    mv Dockerfile.original Dockerfile
    rm -f Dockerfile.prod  # Remover cópia temporária se necessário
    echo -e "${GREEN}✓ Dockerfile restaurado${NC}"
fi

# 8. Deploy no Cloud Run
echo -e "${YELLOW}[7/7] Fazendo deploy no Cloud Run...${NC}"
SERVICE_NAME="monpec"
REGION="us-central1"

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,PYTHONUNBUFFERED=1" \
    --memory=1Gi \
    --cpu=1 \
    --timeout=300 \
    --max-instances=10 \
    --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Deploy concluído${NC}"
else
    echo -e "${RED}✗ Erro no deploy${NC}"
    exit 1
fi
echo ""

# 9. Obter URL do serviço
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format="value(status.url)")

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}URL do serviço:${NC} $SERVICE_URL"
echo ""
echo -e "${YELLOW}Próximos passos:${NC}"
echo ""
echo "1. Aplicar migrações do banco de dados:"
echo "   gcloud run jobs create migrate-monpec \\"
echo "     --image $IMAGE_TAG \\"
echo "     --region $REGION \\"
echo "     --command python \\"
echo "     --args 'manage.py,migrate,--noinput' \\"
echo "     --set-env-vars 'DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'"
echo ""
echo "   gcloud run jobs execute migrate-monpec --region $REGION"
echo ""
echo "2. Configurar variáveis de ambiente (se necessário):"
echo "   gcloud run services update $SERVICE_NAME \\"
echo "     --region $REGION \\"
echo "     --set-env-vars 'SECRET_KEY=SUA_CHAVE_SECRETA,DB_HOST=SEU_HOST,...'"
echo ""
echo "3. Configurar domínio personalizado (opcional):"
echo "   gcloud run domain-mappings create \\"
echo "     --service $SERVICE_NAME \\"
echo "     --domain monpec.com.br \\"
echo "     --region $REGION"
echo ""
echo "4. Acessar console:"
echo "   https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME"
echo ""





