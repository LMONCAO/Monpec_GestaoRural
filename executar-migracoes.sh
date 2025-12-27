#!/bin/bash
# Script para executar migrações do Django no Google Cloud Run
# Este script cria ou executa um job de migração

set -e

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

# Configurações
PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo '')}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-monpec}"
REGION="${CLOUD_RUN_REGION:-us-central1}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
JOB_NAME="migrate-monpec"

echo ""
echo "========================================"
echo "  EXECUTAR MIGRAÇÕES - SISTEMA MONPEC"
echo "========================================"
echo ""

# Verificar projeto
if [ -z "$PROJECT_ID" ]; then
    print_error "PROJECT_ID não definido!"
    echo "Defina com: export GCP_PROJECT=seu-projeto-id"
    exit 1
fi

gcloud config set project "$PROJECT_ID" --quiet

# Obter variáveis de ambiente do serviço
print_step "Obtendo variáveis de ambiente do serviço..."
ENV_VARS=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")

if [ -z "$ENV_VARS" ]; then
    print_warning "Não foi possível obter variáveis de ambiente do serviço"
    print_info "Usando variáveis padrão..."
    ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"
fi

# Obter Cloud SQL connection name do serviço
CLOUD_SQL_CONNECTION=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].env(name=CLOUD_SQL_CONNECTION_NAME).value)" 2>/dev/null || echo "")

# Verificar se job já existe
print_step "Verificando job de migração..."
if gcloud run jobs describe "$JOB_NAME" --region="$REGION" &>/dev/null; then
    print_info "Job já existe. Atualizando..."
    
    # Atualizar job existente
    UPDATE_ARGS=(
        "run" "jobs" "update" "$JOB_NAME"
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
    
    if [ -n "$CLOUD_SQL_CONNECTION" ]; then
        UPDATE_ARGS+=("--set-cloudsql-instances" "$CLOUD_SQL_CONNECTION")
    fi
    
    gcloud "${UPDATE_ARGS[@]}" --quiet
    print_success "Job atualizado"
else
    print_info "Criando novo job de migração..."
    
    # Criar novo job
    CREATE_ARGS=(
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
    
    if [ -n "$CLOUD_SQL_CONNECTION" ]; then
        CREATE_ARGS+=("--set-cloudsql-instances" "$CLOUD_SQL_CONNECTION")
    fi
    
    if gcloud "${CREATE_ARGS[@]}" --quiet; then
        print_success "Job criado"
    else
        print_error "Erro ao criar job!"
        exit 1
    fi
fi

# Executar job
print_step "Executando migrações..."
print_info "Isso pode levar alguns minutos..."

if gcloud run jobs execute "$JOB_NAME" --region="$REGION" --wait; then
    print_success "Migrações aplicadas com sucesso!"
    
    # Mostrar logs
    echo ""
    print_step "Últimos logs do job:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME" \
        --limit=20 \
        --format="table(timestamp,textPayload)" \
        --project="$PROJECT_ID" 2>/dev/null || print_warning "Não foi possível obter logs"
else
    print_error "Erro ao executar migrações!"
    echo ""
    print_info "Para ver os logs do erro, execute:"
    echo "  gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --limit=50 --project=$PROJECT_ID"
    exit 1
fi

echo ""
