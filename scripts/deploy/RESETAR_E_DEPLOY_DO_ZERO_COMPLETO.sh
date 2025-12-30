#!/bin/bash
# 🔥 RESETAR E DEPLOY DO ZERO - GOOGLE CLOUD
# Script completo que reseta tudo e faz deploy do zero
# ⚠️ ATENÇÃO: Este script EXCLUI todos os recursos do projeto antes de fazer deploy!

set -euo pipefail  # Parar em caso de erro, não permitir variáveis não definidas, tratar pipes

# ==========================================
# CONFIGURAÇÕES
# ==========================================
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
DOMAIN="monpec.com.br"
WWW_DOMAIN="www.monpec.com.br"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções auxiliares
print_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se gcloud está instalado
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI não está instalado!"
        echo "Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI encontrado"
}

# Verificar se está autenticado
check_auth() {
    print_info "Verificando autenticação..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "Não autenticado. Fazendo login..."
        gcloud auth login
    fi
    print_success "Autenticado"
}

# Verificar diretório e arquivos locais
check_local_files() {
    print_info "Verificando diretório atual e arquivos locais..."
    
    CURRENT_DIR=$(pwd)
    print_info "Diretório atual: $CURRENT_DIR"
    
    # Verificar se está no diretório do projeto Django
    if [ ! -f "manage.py" ]; then
        print_error "manage.py não encontrado no diretório atual!"
        echo ""
        echo "O script DEVE ser executado no diretório raiz do projeto Django."
        echo "Certifique-se de que você está no diretório que contém:"
        echo "  - manage.py"
        echo "  - Dockerfile.prod ou Dockerfile"
        echo "  - requirements_producao.txt ou requirements.txt"
        echo "  - sistema_rural/ (pasta do Django)"
        echo ""
        echo "Se estiver no Cloud Shell, faça upload dos arquivos do localhost primeiro!"
        exit 1
    fi
    
    # Listar alguns arquivos chave para confirmar
    print_info "Arquivos encontrados no diretório:"
    echo "  ✅ manage.py"
    [ -f "Dockerfile.prod" ] && echo "  ✅ Dockerfile.prod" || echo "  ⚠️  Dockerfile.prod não encontrado"
    [ -f "requirements_producao.txt" ] && echo "  ✅ requirements_producao.txt" || echo "  ⚠️  requirements_producao.txt não encontrado"
    [ -d "sistema_rural" ] && echo "  ✅ sistema_rural/ (pasta Django)" || echo "  ⚠️  sistema_rural/ não encontrada"
    
    # Contar arquivos para dar ideia do tamanho do projeto
    FILE_COUNT=$(find . -type f -name "*.py" | wc -l)
    print_info "Arquivos Python encontrados: $FILE_COUNT"
    
    if [ "$FILE_COUNT" -lt 10 ]; then
        print_warning "Poucos arquivos Python encontrados! Certifique-se de que todos os arquivos do projeto estão aqui."
        read -p "Continuar mesmo assim? (s/N): " confirm_files
        if [ "$confirm_files" != "s" ] && [ "$confirm_files" != "S" ]; then
            print_error "Operação cancelada."
            exit 0
        fi
    fi
    
    print_success "Diretório verificado - os arquivos DESTE diretório serão usados no deploy"
    echo ""
}

# ==========================================
# PARTE 1: CONFIRMAÇÃO E CONFIGURAÇÃO
# ==========================================
print_header "RESETAR E DEPLOY DO ZERO"

echo -e "${RED}⚠️  ATENÇÃO CRÍTICA:${NC}"
echo "Este script vai EXCLUIR todos os recursos do projeto:"
echo "  • Serviços Cloud Run"
echo "  • Jobs Cloud Run"
echo "  • Domain Mappings"
echo "  • Imagens Docker no Container Registry"
echo "  • (Opcional) Instância Cloud SQL e TODOS os dados"
echo ""
echo -e "${YELLOW}Recomendação: Faça backup do banco de dados antes de continuar!${NC}"
echo ""

read -p "Digite 'CONFIRMAR RESETAR TUDO' para continuar: " confirm
if [ "$confirm" != "CONFIRMAR RESETAR TUDO" ]; then
    print_error "Operação cancelada pelo usuário."
    exit 0
fi

echo ""

# Verificações iniciais
check_gcloud
check_auth

# CRÍTICO: Verificar que está usando os arquivos corretos do localhost
check_local_files

print_info "Configurando projeto..."
gcloud config set project "$PROJECT_ID"
print_success "Projeto configurado: $PROJECT_ID"

# Habilitar APIs necessárias
print_info "Habilitando APIs necessárias..."
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

# ==========================================
# PARTE 2: RESETAR/EXCLUIR RECURSOS
# ==========================================

print_header "PARTE 1: EXCLUINDO RECURSOS EXISTENTES"

# 2.1: Excluir Domain Mappings
print_info "Excluindo Domain Mappings..."
gcloud run domain-mappings delete "$DOMAIN" --region "$REGION" --quiet 2>&1 | grep -v "does not exist" || true
gcloud run domain-mappings delete "$WWW_DOMAIN" --region "$REGION" --quiet 2>&1 | grep -v "does not exist" || true
print_success "Domain Mappings excluídos"

# 2.2: Excluir Jobs do Cloud Run
print_info "Excluindo Jobs do Cloud Run..."
ALL_JOBS=$(gcloud run jobs list --region "$REGION" --format="value(name)" 2>/dev/null || echo "")
if [ -n "$ALL_JOBS" ]; then
    while IFS= read -r JOB; do
        if [ -n "$JOB" ]; then
            JOB_SHORT=$(basename "$JOB")
            print_info "  Excluindo job: $JOB_SHORT"
            gcloud run jobs delete "$JOB_SHORT" --region "$REGION" --quiet 2>&1 | grep -v "does not exist" || true
        fi
    done <<< "$ALL_JOBS"
fi
print_success "Jobs excluídos"

# 2.3: Excluir Serviços Cloud Run
print_info "Excluindo Serviços Cloud Run..."
ALL_SERVICES=$(gcloud run services list --region "$REGION" --format="value(name)" 2>/dev/null || echo "")
if [ -n "$ALL_SERVICES" ]; then
    while IFS= read -r SERVICE; do
        if [ -n "$SERVICE" ]; then
            SERVICE_SHORT=$(basename "$SERVICE")
            print_info "  Excluindo serviço: $SERVICE_SHORT"
            gcloud run services delete "$SERVICE_SHORT" --region "$REGION" --quiet 2>&1 | grep -v "does not exist" || true
        fi
    done <<< "$ALL_SERVICES"
fi
print_success "Serviços excluídos"

# 2.4: Excluir Imagens Docker
print_info "Excluindo Imagens Docker do Container Registry..."
REPOSITORY="gcr.io/$PROJECT_ID"

# Listar e excluir todas as imagens
ALL_IMAGES=$(gcloud container images list --repository="$REPOSITORY" --format="value(name)" 2>/dev/null || echo "")
if [ -n "$ALL_IMAGES" ]; then
    while IFS= read -r IMAGE; do
        if [ -n "$IMAGE" ]; then
            print_info "  Excluindo imagem: $IMAGE"
            gcloud container images delete "$IMAGE" --force-delete-tags --quiet 2>&1 | grep -v "does not exist" || true
        fi
    done <<< "$ALL_IMAGES"
fi
print_success "Imagens Docker excluídas"

# 2.5: Perguntar sobre Cloud SQL
echo ""
print_warning "SOBRE O CLOUD SQL (BANCO DE DADOS):"
echo "Você pode excluir o banco de dados (TODOS OS DADOS SERÃO PERDIDOS)"
echo "ou mantê-lo e apenas recriar a estrutura."
echo ""
read -p "Excluir instância Cloud SQL? Digite 'EXCLUIR' para excluir (qualquer outra coisa mantém): " confirm_db

if [ "$confirm_db" = "EXCLUIR" ]; then
    print_info "Excluindo instância Cloud SQL: $INSTANCE_NAME"
    gcloud sql instances delete "$INSTANCE_NAME" --quiet 2>&1 | grep -v "does not exist" || true
    print_warning "⚠️  Instância Cloud SQL excluída - TODOS OS DADOS FORAM PERDIDOS!"
    DB_NEEDS_CREATION=true
else
    print_info "Mantendo instância Cloud SQL existente"
    DB_NEEDS_CREATION=false
    
    # Verificar se a instância existe
    if ! gcloud sql instances describe "$INSTANCE_NAME" &>/dev/null; then
        print_warning "Instância Cloud SQL não encontrada. Será criada automaticamente."
        DB_NEEDS_CREATION=true
    else
        print_info "Configurando senha do usuário do banco..."
        gcloud sql users set-password "$DB_USER" --instance="$INSTANCE_NAME" --password="$DB_PASSWORD" 2>&1 | grep -v "does not exist" || true
        print_success "Senha do banco configurada"
    fi
fi

# ==========================================
# PARTE 3: CRIAR/VERIFICAR CLOUD SQL
# ==========================================

print_header "PARTE 2: CONFIGURANDO CLOUD SQL"

if [ "$DB_NEEDS_CREATION" = true ]; then
    print_info "Criando instância Cloud SQL: $INSTANCE_NAME"
    
    # Verificar se já existe (pode ter sido criada no passo anterior)
    if ! gcloud sql instances describe "$INSTANCE_NAME" &>/dev/null; then
        print_info "Criando instância PostgreSQL (sem --enable-bin-log, pois só funciona para MySQL)..."
        gcloud sql instances create "$INSTANCE_NAME" \
            --database-version=POSTGRES_14 \
            --tier=db-f1-micro \
            --region="$REGION" \
            --backup-start-time=03:00 \
            --storage-type=SSD \
            --storage-size=10GB
        
        print_success "Instância Cloud SQL criada"
        
        # Aguardar instância estar pronta
        print_info "Aguardando instância estar pronta (isso pode levar 3-5 minutos)..."
        gcloud sql instances wait "$INSTANCE_NAME" --timeout=600
        
        # Criar banco de dados
        print_info "Criando banco de dados: $DB_NAME"
        gcloud sql databases create "$DB_NAME" --instance="$INSTANCE_NAME" 2>&1 | grep -v "already exists" || true
        
        # Criar usuário
        print_info "Criando usuário: $DB_USER"
        gcloud sql users create "$DB_USER" \
            --instance="$INSTANCE_NAME" \
            --password="$DB_PASSWORD" 2>&1 | grep -v "already exists" || true
        
        print_success "Banco de dados configurado"
    else
        print_info "Instância já existe, configurando..."
    fi
else
    # Apenas garantir que o banco e usuário existem
    print_info "Verificando banco de dados..."
    gcloud sql databases create "$DB_NAME" --instance="$INSTANCE_NAME" 2>&1 | grep -v "already exists" || true
    
    # Tentar criar usuário (pode já existir)
    gcloud sql users create "$DB_USER" \
        --instance="$INSTANCE_NAME" \
        --password="$DB_PASSWORD" 2>&1 | grep -v "already exists" || true
    
    print_success "Banco de dados verificado"
fi

# ==========================================
# PARTE 4: VERIFICAR ARQUIVOS NECESSÁRIOS
# ==========================================

print_header "PARTE 3: VERIFICANDO ARQUIVOS DO PROJETO"

# Verificar Dockerfile
if [ ! -f "Dockerfile.prod" ] && [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile.prod ou Dockerfile não encontrado!"
    echo "Certifique-se de estar no diretório raiz do projeto."
    exit 1
fi
DOCKERFILE="Dockerfile.prod"
if [ ! -f "$DOCKERFILE" ]; then
    DOCKERFILE="Dockerfile"
fi
print_success "Dockerfile encontrado: $DOCKERFILE"

# Verificar requirements
if [ ! -f "requirements_producao.txt" ] && [ ! -f "requirements.txt" ]; then
    print_error "requirements_producao.txt ou requirements.txt não encontrado!"
    exit 1
fi
REQUIREMENTS="requirements_producao.txt"
if [ ! -f "$REQUIREMENTS" ]; then
    REQUIREMENTS="requirements.txt"
fi
print_success "Requirements encontrado: $REQUIREMENTS"

# Garantir openpyxl no requirements
if ! grep -q "^openpyxl" "$REQUIREMENTS" 2>/dev/null; then
    print_info "Adicionando openpyxl ao requirements..."
    echo "openpyxl>=3.1.5" >> "$REQUIREMENTS"
    print_success "openpyxl adicionado"
fi

# Verificar manage.py
if [ ! -f "manage.py" ]; then
    print_error "manage.py não encontrado!"
    echo "Certifique-se de estar no diretório raiz do projeto Django."
    exit 1
fi
print_success "manage.py encontrado"

# ==========================================
# PARTE 5: BUILD DA IMAGEM DOCKER
# ==========================================

print_header "PARTE 4: BUILD DA IMAGEM DOCKER"

TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
IMAGE_LATEST="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

print_info "Buildando imagem Docker usando arquivos do diretório atual..."
CURRENT_DIR=$(pwd)
print_info "Diretório de origem: $CURRENT_DIR"
print_warning "IMPORTANTE: O build vai usar TODOS os arquivos deste diretório!"
print_warning "Isso pode levar 5-15 minutos, aguarde..."

# Confirmar antes de fazer build
echo ""
print_info "Serão enviados para o build todos os arquivos do diretório atual."
read -p "Confirmar build com os arquivos deste diretório? (s/N): " confirm_build
if [ "$confirm_build" != "s" ] && [ "$confirm_build" != "S" ]; then
    print_error "Build cancelado pelo usuário."
    exit 0
fi
echo ""

# Build da imagem - IMPORTANTE: gcloud builds submit envia TODOS os arquivos do diretório atual
print_info "Iniciando build... (enviando arquivos do diretório atual)"
if [ "$DOCKERFILE" = "Dockerfile.prod" ]; then
    # Tentar usar cloudbuild.yaml se existir, senão usar Dockerfile.prod diretamente
    if [ -f "cloudbuild.yaml" ]; then
        print_info "Usando cloudbuild.yaml para build..."
        gcloud builds submit --tag "$IMAGE_TAG" --tag "$IMAGE_LATEST" --config cloudbuild.yaml 2>&1 || {
            print_warning "Build com cloudbuild.yaml falhou, tentando com Dockerfile.prod..."
            gcloud builds submit --tag "$IMAGE_TAG" --tag "$IMAGE_LATEST" 2>&1
        }
    else
        print_info "Usando Dockerfile.prod para build..."
        gcloud builds submit --tag "$IMAGE_TAG" --tag "$IMAGE_LATEST" 2>&1
    fi
else
    print_info "Usando Dockerfile para build..."
    gcloud builds submit --tag "$IMAGE_TAG" --tag "$IMAGE_LATEST" 2>&1
fi

if [ $? -eq 0 ]; then
    print_success "Build concluído: $IMAGE_TAG"
else
    print_error "Erro no build da imagem!"
    exit 1
fi

# ==========================================
# PARTE 6: DEPLOY NO CLOUD RUN
# ==========================================

print_header "PARTE 5: DEPLOY NO CLOUD RUN"

CONNECTION_NAME="$PROJECT_ID:$REGION:$INSTANCE_NAME"
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DJANGO_SUPERUSER_PASSWORD=L6171r12@@"

print_info "Deployando no Cloud Run..."
print_warning "Isso pode levar 2-5 minutos, aguarde..."

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --add-cloudsql-instances="$CONNECTION_NAME" \
    --set-env-vars "$ENV_VARS" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --max-instances=10 \
    --min-instances=0 \
    --port=8080

if [ $? -eq 0 ]; then
    print_success "Deploy concluído!"
else
    print_error "Erro no deploy!"
    exit 1
fi

# ==========================================
# PARTE 7: OBTER URL E VERIFICAR
# ==========================================

print_header "DEPLOY CONCLUÍDO COM SUCESSO!"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo ""
    echo -e "${GREEN}🔗 URL do Serviço:${NC}"
    echo -e "${CYAN}   $SERVICE_URL${NC}"
    echo ""
    echo -e "${GREEN}📋 Credenciais para Login:${NC}"
    echo "   Username: admin"
    echo "   Senha: L6171r12@@"
    echo ""
    echo -e "${YELLOW}⏱️  Aguarde 1-2 minutos para o serviço inicializar completamente${NC}"
    echo ""
    echo -e "${BLUE}📊 Para ver logs:${NC}"
    echo "   gcloud run services logs read $SERVICE_NAME --region $REGION"
    echo ""
    echo -e "${BLUE}📊 Para verificar status:${NC}"
    echo "   gcloud run services describe $SERVICE_NAME --region $REGION"
    echo ""
else
    print_warning "Não foi possível obter a URL do serviço automaticamente"
    echo "Execute: gcloud run services list --region $REGION"
fi

print_success "🎉 TUDO PRONTO! Sistema resetado e deploy concluído do zero!"
echo ""

