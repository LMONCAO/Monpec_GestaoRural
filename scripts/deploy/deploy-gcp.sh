#!/bin/bash
# Script de Deploy Otimizado para Google Cloud Run - Sistema MONPEC
# Este script faz deploy limpo e robusto do sistema

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
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

# Configurações (podem ser sobrescritas por variáveis de ambiente)
PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo '')}"
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
    print_warning "Não autenticado. Fazendo login..."
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
gcloud config set project "$PROJECT_ID" --quiet
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
    gcloud services enable "$api" --quiet 2>&1 | grep -v "already enabled" || true
done
print_success "APIs habilitadas"

# Verificar Dockerfile
print_step "Verificando Dockerfile..."
if [ ! -f "Dockerfile.prod" ]; then
    print_error "Dockerfile.prod não encontrado!"
    exit 1
fi
print_success "Dockerfile.prod encontrado"

# Verificar requirements.txt
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt não encontrado!"
    exit 1
fi

# Build da imagem Docker
print_step "Fazendo build da imagem Docker..."
print_info "  Imagem: $IMAGE_NAME:latest"
print_info "  Isso pode levar alguns minutos..."

if gcloud builds submit --tag "$IMAGE_NAME:latest" --timeout=20m --quiet; then
    print_success "Build concluído com sucesso"
else
    print_error "Erro no build da imagem!"
    exit 1
fi

# Verificar variáveis de ambiente necessárias
print_step "Verificando variáveis de ambiente..."

# Obter variáveis de ambiente do serviço existente (se houver)
EXISTING_ENV=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")

# Construir lista de variáveis de ambiente
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

# Adicionar variáveis se estiverem definidas
[ -n "$SECRET_KEY" ] && ENV_VARS="$ENV_VARS,SECRET_KEY=$SECRET_KEY" || print_warning "SECRET_KEY não definida"
[ -n "$DB_NAME" ] && ENV_VARS="$ENV_VARS,DB_NAME=$DB_NAME"
[ -n "$DB_USER" ] && ENV_VARS="$ENV_VARS,DB_USER=$DB_USER"
[ -n "$DB_PASSWORD" ] && ENV_VARS="$ENV_VARS,DB_PASSWORD=$DB_PASSWORD"
[ -n "$DB_HOST" ] && ENV_VARS="$ENV_VARS,DB_HOST=$DB_HOST"
[ -n "$CLOUD_SQL_CONNECTION_NAME" ] && ENV_VARS="$ENV_VARS,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME"

# Deploy no Cloud Run
print_step "Fazendo deploy no Cloud Run..."
print_info "  Serviço: $SERVICE_NAME"
print_info "  Região: $REGION"
print_info "  Imagem: $IMAGE_NAME:latest"

# Construir comando de deploy
DEPLOY_ARGS=(
    "run" "deploy" "$SERVICE_NAME"
    "--image" "$IMAGE_NAME:latest"
    "--platform" "managed"
    "--region" "$REGION"
    "--allow-unauthenticated"
    "--set-env-vars" "$ENV_VARS"
    "--memory" "2Gi"
    "--cpu" "2"
    "--timeout" "300"
    "--max-instances" "10"
    "--min-instances" "1"
    "--port" "8080"
)

# Adicionar Cloud SQL connection se definida
if [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
    DEPLOY_ARGS+=("--add-cloudsql-instances" "$CLOUD_SQL_CONNECTION_NAME")
    print_info "  Cloud SQL: $CLOUD_SQL_CONNECTION_NAME"
fi

if gcloud "${DEPLOY_ARGS[@]}" --quiet; then
    print_success "Deploy no Cloud Run concluído!"
else
    print_error "Erro no deploy!"
    exit 1
fi

# Obter URL do serviço
print_step "Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null)
if [ -n "$SERVICE_URL" ]; then
    print_success "Serviço disponível em: $SERVICE_URL"
else
    print_warning "Não foi possível obter a URL do serviço"
fi

# Executar migrações via job (se necessário)
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
    
    JOB_ARGS=(
        "run" "jobs" "create" "$JOB_NAME"
        "--image" "$IMAGE_NAME:latest"
        "--region" "$REGION"
        "--set-env-vars" "$ENV_VARS"
        "--memory" "2Gi"
        "--cpu" "1"
        "--max-retries" "3"
        "--task-timeout" "600"
        "--command" "python"
        "--args" "manage.py,migrate,--noinput"
    )
    
    if [ -n "$CLOUD_SQL_CONNECTION_NAME" ]; then
        JOB_ARGS+=("--set-cloudsql-instances" "$CLOUD_SQL_CONNECTION_NAME")
    fi
    
    if gcloud "${JOB_ARGS[@]}" --quiet; then
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

# Resumo final
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
echo "  3. Se necessário, configure variáveis de ambiente adicionais:"
echo "     gcloud run services update $SERVICE_NAME --region=$REGION --update-env-vars KEY=VALUE"
echo ""
echo "  4. Para executar migrações manualmente:"
echo "     gcloud run jobs execute $JOB_NAME --region=$REGION"
echo ""











