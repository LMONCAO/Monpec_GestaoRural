#!/bin/bash
# Script completo de deploy para Google Cloud Platform
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

# 5. Verificar Dockerfile
echo -e "${YELLOW}[5/7] Verificando Dockerfile...${NC}"
# Priorizar Dockerfile.prod se existir, caso contrário usar Dockerfile
if [ -f "Dockerfile.prod" ]; then
    echo -e "${GREEN}✓ Dockerfile.prod encontrado (será usado)${NC}"
    # Se não existir Dockerfile, criar link simbólico ou copiar
    if [ ! -f "Dockerfile" ]; then
        cp Dockerfile.prod Dockerfile
        echo -e "${GREEN}✓ Dockerfile criado a partir de Dockerfile.prod${NC}"
    fi
elif [ -f "Dockerfile" ]; then
    echo -e "${GREEN}✓ Dockerfile encontrado${NC}"
else
    echo -e "${YELLOW}⚠ Dockerfile não encontrado. Criando Dockerfile básico...${NC}"
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements (tentar requirements.txt ou requirements_producao.txt)
COPY requirements*.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    (pip install --no-cache-dir -r requirements.txt 2>/dev/null || \
     pip install --no-cache-dir -r requirements_producao.txt 2>/dev/null || \
     pip install --no-cache-dir django psycopg2-binary gunicorn python-decouple whitenoise)

# Copiar código
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chmod -R 755 /app/staticfiles /app/media /app/logs

# Coletar arquivos estáticos (tentar durante build)
RUN DJANGO_SETTINGS_MODULE=sistema_rural.settings python manage.py collectstatic --noinput 2>/dev/null || \
    (mkdir -p /app/staticfiles && chmod -R 755 /app/staticfiles)

# Porta padrão do Cloud Run
EXPOSE 8080

# Configurar settings para produção
ENV DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp

# Comando para iniciar o servidor
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - sistema_rural.wsgi:application
EOF
    echo -e "${GREEN}✓ Dockerfile criado${NC}"
fi
echo ""

# 6. Verificar .dockerignore
if [ ! -f ".dockerignore" ]; then
    echo -e "${YELLOW}Criando .dockerignore...${NC}"
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

# gcloud builds submit usa Dockerfile por padrão (não aceita --file)
# Se existe Dockerfile.prod, usar ele renomeando temporariamente
DOCKERFILE_ORIGINAL_EXISTS=false
if [ -f "Dockerfile.prod" ]; then
    echo -e "${CYAN}Usando Dockerfile.prod para build${NC}"
    # Fazer backup do Dockerfile original se existir
    if [ -f "Dockerfile" ]; then
        mv Dockerfile Dockerfile.original
        DOCKERFILE_ORIGINAL_EXISTS=true
    fi
    # Copiar Dockerfile.prod para Dockerfile (gcloud usa Dockerfile por padrão)
    cp Dockerfile.prod Dockerfile
fi

# Executar build (gcloud usa Dockerfile por padrão, sem --file)
gcloud builds submit --tag "$IMAGE_TAG" --quiet
BUILD_EXIT_CODE=$?

# Restaurar Dockerfile original se fizemos backup
if [ "$DOCKERFILE_ORIGINAL_EXISTS" = true ] && [ -f "Dockerfile.original" ]; then
    mv Dockerfile.original Dockerfile
    echo -e "${GREEN}✓ Dockerfile original restaurado${NC}"
elif [ -f "Dockerfile.prod" ] && [ ! -f "Dockerfile.original" ]; then
    # Se só usamos Dockerfile.prod e não havia Dockerfile original, manter como está
    echo -e "${CYAN}✓ Dockerfile criado a partir de Dockerfile.prod${NC}"
fi

# Verificar resultado do build
if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Build concluído${NC}"
else
    echo -e "${RED}✗ Erro no build${NC}"
    # Restaurar Dockerfile original em caso de erro
    if [ "$DOCKERFILE_ORIGINAL_EXISTS" = true ] && [ -f "Dockerfile.original" ]; then
        mv Dockerfile.original Dockerfile
    fi
    exit 1
fi
echo ""

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

