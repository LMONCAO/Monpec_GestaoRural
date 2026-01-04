#!/bin/bash
# Script para configurar Google Cloud Storage para imagens do MONPEC
# Este script cria o bucket e configura as permissões necessárias

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_step() { echo -e "${BLUE}▶️  $1${NC}"; }

echo ""
echo "=========================================="
echo "  CONFIGURAR CLOUD STORAGE PARA IMAGENS"
echo "  Sistema MONPEC"
echo "=========================================="
echo ""

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
fi
print_success "Autenticado"

# Obter projeto atual
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    print_error "Nenhum projeto configurado!"
    echo "Configure com: gcloud config set project SEU_PROJECT_ID"
    exit 1
fi
print_info "Projeto: $PROJECT_ID"

# Nome do bucket (pode ser customizado)
BUCKET_NAME="${1:-monpec-media}"
REGION="${2:-us-central1}"

echo ""
print_step "Configurando bucket: $BUCKET_NAME"

# Verificar se o bucket já existe
if gsutil ls -b "gs://$BUCKET_NAME" &>/dev/null; then
    print_warning "Bucket $BUCKET_NAME já existe!"
    read -p "Deseja continuar e atualizar as permissões? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        print_info "Operação cancelada"
        exit 0
    fi
else
    # Criar bucket
    print_step "Criando bucket $BUCKET_NAME na região $REGION..."
    gsutil mb -l "$REGION" "gs://$BUCKET_NAME" || {
        print_error "Erro ao criar bucket. Verifique se o nome é único."
        exit 1
    }
    print_success "Bucket criado"
fi

# Configurar permissões públicas para leitura (necessário para servir imagens)
print_step "Configurando permissões públicas de leitura..."
gsutil iam ch allUsers:objectViewer "gs://$BUCKET_NAME" || {
    print_warning "Não foi possível configurar permissão pública. Tentando método alternativo..."
    # Método alternativo: usar ACL
    gsutil -m acl ch -u AllUsers:R "gs://$BUCKET_NAME" || {
        print_error "Erro ao configurar permissões"
        exit 1
    }
}
print_success "Permissões configuradas"

# Configurar CORS para permitir acesso via web
print_step "Configurando CORS..."
cat > /tmp/cors.json << EOF
[
  {
    "origin": ["https://monpec.com.br", "https://www.monpec.com.br", "http://localhost:8000"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Content-Length"],
    "maxAgeSeconds": 3600
  }
]
EOF
gsutil cors set /tmp/cors.json "gs://$BUCKET_NAME"
rm /tmp/cors.json
print_success "CORS configurado"

# Configurar lifecycle (opcional - manter arquivos por 1 ano)
print_step "Configurando lifecycle do bucket..."
cat > /tmp/lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 3650}
      }
    ]
  }
}
EOF
gsutil lifecycle set /tmp/lifecycle.json "gs://$BUCKET_NAME"
rm /tmp/lifecycle.json
print_success "Lifecycle configurado (arquivos serão mantidos por 10 anos)"

# Verificar permissões da service account do Cloud Run
print_step "Verificando permissões da service account do Cloud Run..."
SERVICE_ACCOUNT=$(gcloud iam service-accounts list --filter="displayName:Cloud Run" --format="value(email)" | head -n 1)
if [ -z "$SERVICE_ACCOUNT" ]; then
    # Tentar formato padrão
    SERVICE_ACCOUNT="${PROJECT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
    print_info "Usando service account padrão: $SERVICE_ACCOUNT"
else
    print_info "Service account encontrada: $SERVICE_ACCOUNT"
fi

# Dar permissões à service account
print_step "Configurando permissões da service account..."
gsutil iam ch "serviceAccount:${SERVICE_ACCOUNT}:objectAdmin" "gs://$BUCKET_NAME" || {
    print_warning "Não foi possível configurar permissões da service account automaticamente"
    print_info "Configure manualmente: gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:objectAdmin gs://$BUCKET_NAME"
}

echo ""
print_success "=========================================="
print_success "  CONFIGURAÇÃO CONCLUÍDA!"
print_success "=========================================="
echo ""
print_info "Bucket: gs://$BUCKET_NAME"
print_info "Região: $REGION"
echo ""
print_step "Próximos passos:"
echo "1. Configure as variáveis de ambiente no Cloud Run:"
echo "   USE_CLOUD_STORAGE=True"
echo "   GS_BUCKET_NAME=$BUCKET_NAME"
echo ""
echo "2. Faça deploy novamente do seu serviço"
echo ""
echo "3. Teste fazendo upload de uma imagem"
echo ""
echo "4. Verifique em: https://monpec.com.br/diagnostico-imagens/"
