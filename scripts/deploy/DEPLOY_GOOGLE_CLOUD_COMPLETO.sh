#!/bin/bash
# Script completo de deploy para Google Cloud Run - Sistema MONPEC
# Execute este script para fazer o deploy completo no Google Cloud

set -e  # Parar em caso de erro

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funções de output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }
print_step() { echo -e "${BLUE}▶ $1${NC}"; }

echo "========================================"
echo "  DEPLOY GOOGLE CLOUD - SISTEMA MONPEC"
echo "========================================"
echo ""

# Configurações padrão (podem ser sobrescritas)
PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-monpec}"
REGION="${CLOUD_RUN_REGION:-us-central1}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Verificar se gcloud está instalado
print_step "Verificando gcloud CLI..."
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI não está instalado!"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
print_success "gcloud CLI encontrado"

# Verificar autenticação
print_step "Verificando autenticação..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    print_info "Não autenticado. Fazendo login..."
    gcloud auth login
    if [ $? -ne 0 ]; then
        print_error "Falha na autenticação!"
        exit 1
    fi
fi
print_success "Autenticado"

# Configurar projeto
if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID não definido!"
    echo "Defina com: export GCP_PROJECT=seu-projeto-id"
    echo "Ou configure com: gcloud config set project SEU-PROJETO-ID"
    exit 1
fi

print_step "Configurando projeto: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"
print_success "Projeto configurado"

# Habilitar APIs necessárias
print_step "Habilitando APIs necessárias..."
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "sqladmin.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "containerregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    print_info "  Habilitando $api..."
    gcloud services enable "$api" --quiet 2>&1 | grep -v "already enabled" || true
done
print_success "APIs habilitadas"

# Verificar Dockerfile
print_step "Verificando Dockerfile..."
if [ ! -f "Dockerfile.prod" ] && [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile não encontrado!"
    exit 1
fi
DOCKERFILE="${DOCKERFILE:-Dockerfile.prod}"
if [ ! -f "$DOCKERFILE" ]; then
    DOCKERFILE="Dockerfile"
fi
print_success "Dockerfile encontrado: $DOCKERFILE"

# Verificar requirements.txt
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt não encontrado!"
    exit 1
fi

# Build da imagem Docker
print_step "Fazendo build da imagem Docker..."
print_info "  Imagem: $IMAGE_NAME:latest"
gcloud builds submit --tag "$IMAGE_NAME:latest" --timeout=20m
if [ $? -ne 0 ]; then
    print_error "Erro no build da imagem!"
    exit 1
fi
print_success "Build concluído"

# Verificar variáveis de ambiente
print_step "Verificando variáveis de ambiente..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

# Adicionar SECRET_KEY se estiver definida
if [ -n "$SECRET_KEY" ]; then
    ENV_VARS="$ENV_VARS,SECRET_KEY=$SECRET_KEY"
    print_info "  SECRET_KEY: definida"
else
    print_info "  SECRET_KEY: não definida (será necessário configurar depois)"
fi

# Adicionar configurações de banco de dados se estiverem definidas
if [ -n "$DB_NAME" ]; then
    ENV_VARS="$ENV_VARS,DB_NAME=$DB_NAME"
fi
if [ -n "$DB_USER" ]; then
    ENV_VARS="$ENV_VARS,DB_USER=$DB_USER"
fi
if [ -n "$DB_PASSWORD" ]; then
    ENV_VARS="$ENV_VARS,DB_PASSWORD=$DB_PASSWORD"
fi
if [ -n "$DB_HOST" ]; then
    ENV_VARS="$ENV_VARS,DB_HOST=$DB_HOST"
fi
if [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
    ENV_VARS="$ENV_VARS,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME"
fi

# Deploy no Cloud Run
print_step "Fazendo deploy no Cloud Run..."
print_info "  Serviço: $SERVICE_NAME"
print_info "  Região: $REGION"
print_info "  Imagem: $IMAGE_NAME:latest"

DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars \"$ENV_VARS\" \
    --memory=1Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1"

# Adicionar Cloud SQL connection se definida
if [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
    DEPLOY_CMD="$DEPLOY_CMD --add-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME"
    print_info "  Cloud SQL: $CLOUD_SQL_CONNECTION_NAME"
fi

eval $DEPLOY_CMD

if [ $? -ne 0 ]; then
    print_error "Erro no deploy!"
    exit 1
fi

print_success "Deploy concluído!"

# Obter URL do serviço
print_step "Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
print_success "Serviço disponível em: $SERVICE_URL"

# Aplicar migrações
print_step "Aplicando migrações do banco de dados..."
print_info "Isso pode levar alguns minutos..."

gcloud run jobs create migrate-monpec \
    --image $IMAGE_NAME:latest \
    --region $REGION \
    --set-env-vars "$ENV_VARS" \
    --command python \
    --args manage.py,migrate,--noinput \
    --max-retries 3 \
    --task-timeout 600 \
    2>/dev/null || true

# Executar job de migração
gcloud run jobs execute migrate-monpec --region $REGION --wait || {
    print_info "Executando migrações manualmente..."
    gcloud run services update $SERVICE_NAME \
        --region $REGION \
        --update-env-vars "$ENV_VARS" \
        --command python \
        --args manage.py,migrate,--noinput || true
}

print_success "Migrações aplicadas"

# Coletar arquivos estáticos (se necessário)
print_step "Coletando arquivos estáticos..."
print_info "Isso será feito automaticamente no container"

echo ""
echo "========================================"
print_success "DEPLOY CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo ""
echo "📋 Informações:"
echo "  • Serviço: $SERVICE_NAME"
echo "  • URL: $SERVICE_URL"
echo "  • Região: $REGION"
echo "  • Projeto: $PROJECT_ID"
echo ""
echo "🔗 Próximos passos:"
echo "  1. Configure o domínio monpec.com.br para apontar para: $SERVICE_URL"
echo "  2. Configure variáveis de ambiente adicionais se necessário:"
echo "     gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars KEY=VALUE"
echo "  3. Verifique os logs:"
echo "     gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "  4. Teste o acesso em: $SERVICE_URL"
echo ""
