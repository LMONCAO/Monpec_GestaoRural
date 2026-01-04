#!/bin/bash
# Script de Bootstrap do Google Cloud Platform para Monpec_GestaoRural
# Este script configura Cloud SQL, Service Account, permissões e GitHub Secrets

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
echo "  BOOTSTRAP GOOGLE CLOUD PLATFORM"
echo "  Sistema Monpec_GestaoRural"
echo "========================================"
echo ""

# Verificar se gcloud está instalado
print_step "Verificando gcloud CLI..."
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI não está instalado!"
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

# Configurações padrão
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
SERVICE_ACCOUNT_NAME="monpec-cloudrun-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Verificar parâmetros
SET_GITHUB_SECRETS=false
GITHUB_REPO=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --set-github-secrets)
            SET_GITHUB_SECRETS=true
            shift
            ;;
        --repo)
            GITHUB_REPO="$2"
            shift 2
            ;;
        *)
            print_warning "Parâmetro desconhecido: $1"
            shift
            ;;
    esac
done

# Configurar projeto
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
    "secretmanager.googleapis.com"
    "iam.googleapis.com"
)

for api in "${APIS[@]}"; do
    gcloud services enable "$api" --quiet 2>&1 | grep -v "already enabled" || true
done
print_success "APIs habilitadas"

# Criar Cloud SQL instance (se não existir)
print_step "Verificando Cloud SQL instance..."
if gcloud sql instances describe "$DB_INSTANCE" &>/dev/null; then
    print_info "Cloud SQL instance '$DB_INSTANCE' já existe"
else
    print_info "Criando Cloud SQL instance '$DB_INSTANCE'..."
    gcloud sql instances create "$DB_INSTANCE" \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region="$REGION" \
        --quiet
    
    print_success "Cloud SQL instance criada"
fi

# Obter connection name
CLOUD_SQL_CONNECTION_NAME=$(gcloud sql instances describe "$DB_INSTANCE" --format="value(connectionName)")
print_info "Cloud SQL Connection Name: $CLOUD_SQL_CONNECTION_NAME"

# Criar banco de dados (se não existir)
print_step "Verificando banco de dados '$DB_NAME'..."
if gcloud sql databases describe "$DB_NAME" --instance="$DB_INSTANCE" &>/dev/null; then
    print_info "Banco de dados '$DB_NAME' já existe"
else
    print_info "Criando banco de dados '$DB_NAME'..."
    gcloud sql databases create "$DB_NAME" \
        --instance="$DB_INSTANCE" \
        --quiet
    print_success "Banco de dados criado"
fi

# Gerar senha do banco (ou usar existente)
print_step "Configurando usuário do banco de dados..."
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

# Verificar se usuário existe
if gcloud sql users list --instance="$DB_INSTANCE" --format="value(name)" | grep -q "^${DB_USER}$"; then
    print_info "Usuário '$DB_USER' já existe. Atualizando senha..."
    gcloud sql users set-password "$DB_USER" \
        --instance="$DB_INSTANCE" \
        --password="$DB_PASSWORD" \
        --quiet
else
    print_info "Criando usuário '$DB_USER'..."
    gcloud sql users create "$DB_USER" \
        --instance="$DB_INSTANCE" \
        --password="$DB_PASSWORD" \
        --quiet
fi
print_success "Usuário do banco configurado"

# Gerar SECRET_KEY do Django
SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-20)

# Criar Service Account (se não existir)
print_step "Verificando Service Account..."
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" &>/dev/null; then
    print_info "Service Account '$SERVICE_ACCOUNT_NAME' já existe"
else
    print_info "Criando Service Account '$SERVICE_ACCOUNT_NAME'..."
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="Monpec Cloud Run Service Account" \
        --description="Service Account para Cloud Run do sistema Monpec" \
        --quiet
    print_success "Service Account criada"
fi

# Conceder permissões necessárias
print_step "Configurando permissões do Service Account..."
ROLES=(
    "roles/cloudsql.client"
    "roles/run.invoker"
    "roles/storage.objectViewer"
    "roles/secretmanager.secretAccessor"
)

for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="$role" \
        --quiet 2>&1 | grep -v "etag" || true
done
print_success "Permissões configuradas"

# Criar chave JSON do Service Account
print_step "Criando chave JSON do Service Account..."
KEY_FILE="/tmp/monpec-sa-key.json"
gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SERVICE_ACCOUNT_EMAIL" \
    --quiet
print_success "Chave JSON criada"

# Ler conteúdo da chave para GitHub Secrets
GCP_SA_KEY=$(cat "$KEY_FILE" | base64 -w 0)

# Configurar GitHub Secrets (se solicitado)
if [ "$SET_GITHUB_SECRETS" = true ]; then
    if [ -z "$GITHUB_REPO" ]; then
        print_error "Parâmetro --repo é obrigatório quando --set-github-secrets é usado"
        exit 1
    fi
    
    print_step "Configurando GitHub Secrets..."
    print_warning "Para configurar GitHub Secrets, você precisa do GitHub CLI (gh) instalado e autenticado"
    print_warning "Ou configure manualmente no GitHub: https://github.com/$GITHUB_REPO/settings/secrets/actions"
    echo ""
    
    if command -v gh &> /dev/null; then
        print_info "GitHub CLI encontrado. Configurando secrets..."
        
        # Verificar autenticação do GitHub CLI
        if ! gh auth status &>/dev/null; then
            print_warning "GitHub CLI não autenticado. Execute: gh auth login"
        else
            # Configurar secrets
            echo "$GCP_SA_KEY" | gh secret set GCP_SA_KEY --repo "$GITHUB_REPO"
            echo "$SECRET_KEY" | gh secret set SECRET_KEY --repo "$GITHUB_REPO"
            echo "$DB_NAME" | gh secret set DB_NAME --repo "$GITHUB_REPO"
            echo "$DB_USER" | gh secret set DB_USER --repo "$GITHUB_REPO"
            echo "$DB_PASSWORD" | gh secret set DB_PASSWORD --repo "$GITHUB_REPO"
            echo "$DJANGO_SUPERUSER_PASSWORD" | gh secret set DJANGO_SUPERUSER_PASSWORD --repo "$GITHUB_REPO"
            
            print_success "GitHub Secrets configurados!"
        fi
    else
        print_warning "GitHub CLI não encontrado. Configure os secrets manualmente:"
        echo ""
        echo "Repositório: $GITHUB_REPO"
        echo "URL: https://github.com/$GITHUB_REPO/settings/secrets/actions"
        echo ""
        echo "Secrets a configurar:"
        echo "  GCP_SA_KEY: (conteúdo do arquivo $KEY_FILE em base64)"
        echo "  SECRET_KEY: $SECRET_KEY"
        echo "  DB_NAME: $DB_NAME"
        echo "  DB_USER: $DB_USER"
        echo "  DB_PASSWORD: $DB_PASSWORD"
        echo "  DJANGO_SUPERUSER_PASSWORD: $DJANGO_SUPERUSER_PASSWORD"
        echo ""
    fi
fi

# Limpar arquivo temporário
rm -f "$KEY_FILE"

# Resumo final
echo ""
echo "========================================"
print_success "BOOTSTRAP CONCLUÍDO COM SUCESSO!"
echo "========================================"
echo ""
echo "📋 Informações da configuração:"
echo "  • Projeto: $PROJECT_ID"
echo "  • Região: $REGION"
echo "  • Cloud SQL Instance: $DB_INSTANCE"
echo "  • Cloud SQL Connection: $CLOUD_SQL_CONNECTION_NAME"
echo "  • Database: $DB_NAME"
echo "  • Database User: $DB_USER"
echo "  • Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""
echo "🔑 Credenciais geradas:"
echo "  • DB_PASSWORD: $DB_PASSWORD"
echo "  • SECRET_KEY: $SECRET_KEY"
echo "  • DJANGO_SUPERUSER_PASSWORD: $DJANGO_SUPERUSER_PASSWORD"
echo ""
if [ "$SET_GITHUB_SECRETS" = false ]; then
    echo "⚠️  IMPORTANTE: Salve essas credenciais em local seguro!"
    echo "   Para configurar GitHub Secrets depois, execute:"
    echo "   bash deploy/gcp/bootstrap_gcp.sh --set-github-secrets --repo $GITHUB_REPO"
    echo ""
fi
echo "🚀 Próximos passos:"
echo "  1. As credenciais foram configuradas no Google Cloud"
if [ "$SET_GITHUB_SECRETS" = true ]; then
    echo "  2. GitHub Secrets configurados"
else
    echo "  2. Configure os GitHub Secrets manualmente se necessário"
fi
echo "  3. O sistema está pronto para deploy!"
echo ""


