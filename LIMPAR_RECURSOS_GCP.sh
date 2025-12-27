#!/bin/bash
# 🗑️ SCRIPT DE LIMPEZA DE RECURSOS GCP
# Remove todos os recursos antigos do Google Cloud Platform
# Projeto: monpec-sistema-rural

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    error "gcloud CLI não está instalado!"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo ""
echo "========================================"
echo "🗑️  LIMPEZA DE RECURSOS GCP - MONPEC"
echo "========================================"
echo ""
warning "ATENÇÃO: Este script vai DELETAR recursos do Google Cloud!"
warning "Certifique-se de ter feito backup dos dados importantes!"
echo ""

# Verificar projeto
log "Verificando projeto atual..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    warning "Projeto atual: $CURRENT_PROJECT"
    read -p "Deseja configurar para $PROJECT_ID? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        gcloud config set project $PROJECT_ID
        success "Projeto configurado!"
    else
        error "Operação cancelada!"
        exit 1
    fi
else
    success "Projeto correto: $PROJECT_ID"
fi
echo ""

# Confirmação final
warning "Você está prestes a DELETAR:"
echo "  - Serviço Cloud Run: $SERVICE_NAME"
echo "  - Jobs do Cloud Run relacionados"
echo "  - Instância Cloud SQL: $INSTANCE_NAME (com confirmação)"
echo "  - Imagens Docker antigas"
echo "  - Domain mappings"
echo ""
read -p "Tem CERTEZA que deseja continuar? Digite 'CONFIRMAR' para prosseguir: " CONFIRM
if [ "$CONFIRM" != "CONFIRMAR" ]; then
    error "Operação cancelada!"
    exit 1
fi
echo ""

# 1. DELETAR SERVIÇO CLOUD RUN
log "1/5 - Deletando serviço Cloud Run..."
if gcloud run services describe $SERVICE_NAME --region $REGION &>/dev/null; then
    gcloud run services delete $SERVICE_NAME --region $REGION --quiet
    success "Serviço Cloud Run deletado!"
else
    warning "Serviço Cloud Run não encontrado (já foi deletado ou não existe)"
fi
echo ""

# 2. DELETAR JOBS DO CLOUD RUN
log "2/5 - Deletando jobs do Cloud Run..."
JOBS=$(gcloud run jobs list --region $REGION --format="value(name)" 2>/dev/null | grep -i monpec || true)
if [ -n "$JOBS" ]; then
    for JOB in $JOBS; do
        log "  Deletando job: $JOB"
        gcloud run jobs delete $JOB --region $REGION --quiet 2>/dev/null || true
    done
    success "Jobs deletados!"
else
    warning "Nenhum job encontrado"
fi
echo ""

# 3. DELETAR INSTÂNCIA CLOUD SQL (COM CONFIRMAÇÃO)
log "3/5 - Verificando instância Cloud SQL..."
if gcloud sql instances describe $INSTANCE_NAME &>/dev/null; then
    warning "⚠️  ATENÇÃO: Você está prestes a DELETAR o banco de dados!"
    warning "⚠️  TODOS OS DADOS SERÃO PERDIDOS PERMANENTEMENTE!"
    echo ""
    read -p "Digite 'DELETAR BANCO' para confirmar a exclusão do banco: " CONFIRM_DB
    if [ "$CONFIRM_DB" = "DELETAR BANCO" ]; then
        log "  Deletando instância Cloud SQL: $INSTANCE_NAME"
        gcloud sql instances delete $INSTANCE_NAME --quiet
        success "Instância Cloud SQL deletada!"
    else
        warning "Exclusão do banco cancelada (banco mantido)"
    fi
else
    warning "Instância Cloud SQL não encontrada (já foi deletada ou não existe)"
fi
echo ""

# 4. DELETAR IMAGENS DOCKER ANTIGAS
log "4/5 - Deletando imagens Docker antigas..."
IMAGE_NAME="gcr.io/$PROJECT_ID/monpec"
IMAGES=$(gcloud container images list-tags $IMAGE_NAME --format="value(digest)" 2>/dev/null || true)
if [ -n "$IMAGES" ]; then
    IMAGE_COUNT=$(echo "$IMAGES" | wc -l)
    log "  Encontradas $IMAGE_COUNT imagens antigas"
    read -p "Deseja deletar todas as imagens antigas? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        for DIGEST in $IMAGES; do
            gcloud container images delete $IMAGE_NAME@$DIGEST --quiet 2>/dev/null || true
        done
        success "Imagens Docker deletadas!"
    else
        warning "Imagens mantidas"
    fi
else
    warning "Nenhuma imagem encontrada"
fi
echo ""

# 5. DELETAR DOMAIN MAPPINGS
log "5/5 - Deletando domain mappings..."
DOMAINS=$(gcloud run domain-mappings list --region $REGION --format="value(name)" 2>/dev/null || true)
if [ -n "$DOMAINS" ]; then
    for DOMAIN in $DOMAINS; do
        log "  Deletando domain mapping: $DOMAIN"
        gcloud run domain-mappings delete $DOMAIN --region $REGION --quiet 2>/dev/null || true
    done
    success "Domain mappings deletados!"
else
    warning "Nenhum domain mapping encontrado"
fi
echo ""

# RESUMO
echo ""
echo "========================================"
success "LIMPEZA CONCLUÍDA!"
echo "========================================"
echo ""
log "Recursos deletados:"
echo "  ✅ Serviço Cloud Run"
echo "  ✅ Jobs do Cloud Run"
echo "  ✅ Instância Cloud SQL (se confirmado)"
echo "  ✅ Imagens Docker antigas (se confirmado)"
echo "  ✅ Domain mappings"
echo ""
warning "Próximo passo: Execute INSTALAR_DO_ZERO.sh para criar tudo do zero"
echo ""
















