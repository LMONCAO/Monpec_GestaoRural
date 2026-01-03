#!/bin/bash
# Script completo de deploy para Google Cloud Shell
# Copie e cole todo este código no Cloud Shell

set -e  # Parar em caso de erro

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}→ $1${NC}"; }
print_step() { echo -e "${BLUE}▶ $1${NC}"; }

echo ""
echo "========================================"
echo "  DEPLOY GOOGLE CLOUD - SISTEMA MONPEC"
echo "========================================"
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Variáveis de ambiente
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

# Configurar projeto
print_step "Configurando projeto: $PROJECT_ID"
gcloud config set project "$PROJECT_ID" --quiet
print_success "Projeto configurado"

# Habilitar APIs necessárias
print_step "Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
print_success "APIs habilitadas"

# Verificar Dockerfile
print_step "Verificando Dockerfile..."
if [ ! -f "Dockerfile.prod" ]; then
    print_error "Dockerfile.prod não encontrado!"
    exit 1
fi
print_success "Dockerfile.prod encontrado"

# Build da imagem Docker
print_step "Fazendo build da imagem Docker..."
print_info "  Imagem: $IMAGE_NAME:latest"
print_info "  Isso pode levar 5-10 minutos..."
echo ""

if gcloud builds submit --tag "$IMAGE_NAME:latest" --timeout=20m; then
    print_success "Build concluído com sucesso"
else
    print_error "Erro no build da imagem!"
    exit 1
fi

echo ""

# Deploy no Cloud Run
print_step "Fazendo deploy no Cloud Run..."
print_info "  Serviço: $SERVICE_NAME"
print_info "  Região: $REGION"
print_info "  Imagem: $IMAGE_NAME:latest"
echo ""

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "$ENV_VARS" \
    --add-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080 \
    --quiet

if [ $? -eq 0 ]; then
    print_success "Deploy no Cloud Run concluído!"
else
    print_error "Erro no deploy!"
    exit 1
fi

echo ""

# Obter URL do serviço
print_step "Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    print_success "Serviço disponível em: $SERVICE_URL"
else
    print_warning "Não foi possível obter a URL do serviço"
fi

echo ""

# Executar migrações
print_step "Aplicando migrações do banco de dados..."
JOB_NAME="migrate-monpec"

# Verificar se job já existe
if gcloud run jobs describe "$JOB_NAME" --region="$REGION" &>/dev/null; then
    print_info "Job de migração já existe. Executando..."
    if gcloud run jobs execute "$JOB_NAME" --region="$REGION" --wait; then
        print_success "Migrações aplicadas com sucesso!"
    else
        print_warning "Erro ao executar migrações. Tente executar manualmente:"
        print_info "  gcloud run jobs execute $JOB_NAME --region=$REGION"
    fi
else
    print_info "Criando job de migração..."
    
    gcloud run jobs create "$JOB_NAME" \
        --image "$IMAGE_NAME:latest" \
        --region "$REGION" \
        --set-env-vars "$ENV_VARS" \
        --set-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" \
        --memory 2Gi \
        --cpu 1 \
        --max-retries 3 \
        --task-timeout 600 \
        --command python \
        --args "manage.py,migrate,--noinput" \
        --quiet
    
    if [ $? -eq 0 ]; then
        print_success "Job de migração criado"
        if gcloud run jobs execute "$JOB_NAME" --region="$REGION" --wait; then
            print_success "Migrações aplicadas com sucesso!"
        else
            print_warning "Erro ao executar migrações. Tente executar manualmente:"
            print_info "  gcloud run jobs execute $JOB_NAME --region=$REGION"
        fi
    else
        print_warning "Não foi possível criar job de migração"
        print_info "Execute as migrações manualmente após o deploy"
    fi
fi

echo ""
echo "========================================"
print_success "DEPLOY CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo ""
echo "📋 Informações:"
echo "  • Serviço: $SERVICE_NAME"
[ -n "$SERVICE_URL" ] && echo "  • URL: $SERVICE_URL"
echo "  • Região: $REGION"
echo "  • Projeto: $PROJECT_ID"
echo ""
echo "🔗 Próximos passos:"
echo "  1. Verifique os logs:"
echo "     gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"
echo ""
if [ -n "$SERVICE_URL" ]; then
    echo "  2. Teste o acesso em: $SERVICE_URL"
    echo ""
fi
echo "  3. Para executar migrações manualmente (se necessário):"
echo "     gcloud run jobs execute $JOB_NAME --region=$REGION"
echo ""











