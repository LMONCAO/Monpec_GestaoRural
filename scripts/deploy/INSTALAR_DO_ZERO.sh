#!/bin/bash
# 🚀 SCRIPT DE INSTALAÇÃO DO ZERO - GCP
# Instala tudo do zero no Google Cloud Platform
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
DB_NAME="monpec_db"
DB_USER="monpec_user"
IMAGE_NAME="gcr.io/$PROJECT_ID/monpec"

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
echo "🚀 INSTALAÇÃO DO ZERO - MONPEC GCP"
echo "========================================"
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

# Habilitar APIs necessárias
log "Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable sql-component.googleapis.com --quiet
success "APIs habilitadas!"
echo ""

# Solicitar senha do banco
warning "Você precisará fornecer uma senha para o banco de dados."
warning "A senha deve ter no mínimo 8 caracteres."
read -sp "Digite a senha do banco de dados: " DB_PASSWORD
echo ""
if [ ${#DB_PASSWORD} -lt 8 ]; then
    error "Senha deve ter no mínimo 8 caracteres!"
    exit 1
fi
echo ""

# Solicitar SECRET_KEY do Django
warning "Você pode fornecer uma SECRET_KEY do Django ou deixar gerar automaticamente."
read -p "Deseja fornecer SECRET_KEY? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    read -sp "Digite a SECRET_KEY: " SECRET_KEY
    echo ""
else
    # Gerar SECRET_KEY automaticamente
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 50)
    success "SECRET_KEY gerada automaticamente"
fi
echo ""

# 1. CRIAR INSTÂNCIA CLOUD SQL
log "1/6 - Criando instância Cloud SQL PostgreSQL 15..."
if gcloud sql instances describe $INSTANCE_NAME &>/dev/null; then
    warning "Instância Cloud SQL já existe: $INSTANCE_NAME"
    read -p "Deseja usar a instância existente? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        error "Operação cancelada! Delete a instância existente primeiro."
        exit 1
    fi
else
    log "  Criando instância PostgreSQL 15..."
    gcloud sql instances create $INSTANCE_NAME \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=$DB_PASSWORD \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase \
        --backup-start-time=03:00 \
        --enable-bin-log \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=4 \
        --quiet
    
    success "Instância Cloud SQL criada!"
fi
echo ""

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
log "Connection name: $CONNECTION_NAME"
echo ""

# 2. CRIAR BANCO DE DADOS E USUÁRIO
log "2/6 - Criando banco de dados e usuário..."
# Criar banco de dados
gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --quiet || warning "Banco já existe"
# Criar usuário
gcloud sql users create $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASSWORD \
    --quiet || warning "Usuário já existe"
success "Banco de dados e usuário criados!"
echo ""

# 3. BUILD DA IMAGEM DOCKER
log "3/6 - Fazendo build da imagem Docker..."
log "  Isso pode levar alguns minutos..."
gcloud builds submit --tag $IMAGE_NAME --timeout=600s
success "Imagem Docker criada!"
echo ""

# 4. DEPLOY NO CLOUD RUN
log "4/6 - Fazendo deploy no Cloud Run..."
log "  Configurando variáveis de ambiente e recursos..."

# Construir lista de variáveis de ambiente
ENV_VARS="DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

# Adicionar variáveis opcionais se fornecidas
read -p "Deseja configurar Mercado Pago agora? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    read -p "Digite MERCADOPAGO_ACCESS_TOKEN: " MP_TOKEN
    read -p "Digite MERCADOPAGO_PUBLIC_KEY: " MP_PUBLIC_KEY
    ENV_VARS="$ENV_VARS,MERCADOPAGO_ACCESS_TOKEN=$MP_TOKEN,MERCADOPAGO_PUBLIC_KEY=$MP_PUBLIC_KEY"
fi

# Fazer deploy
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars $ENV_VARS \
    --memory 4Gi \
    --cpu 2 \
    --timeout 600 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080 \
    --quiet

success "Deploy no Cloud Run concluído!"
echo ""

# Obter URL do serviço
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
log "URL do serviço: $SERVICE_URL"
echo ""

# 5. APLICAR MIGRAÇÕES
log "5/6 - Aplicando migrações do Django..."
log "  Criando job de migração..."

# Criar job para migrações
JOB_NAME="migrate-monpec"
gcloud run jobs create $JOB_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --set-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars $ENV_VARS \
    --memory 2Gi \
    --cpu 1 \
    --max-retries 3 \
    --task-timeout 600 \
    --command python \
    --args "manage.py,migrate,--noinput" \
    --quiet || warning "Job já existe"

# Executar job
log "  Executando migrações..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait
success "Migrações aplicadas!"
echo ""

# 6. COLETAR ARQUIVOS ESTÁTICOS
log "6/6 - Coletando arquivos estáticos..."
log "  Criando job para collectstatic..."

STATIC_JOB_NAME="collectstatic-monpec"
gcloud run jobs create $STATIC_JOB_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --set-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars $ENV_VARS \
    --memory 2Gi \
    --cpu 1 \
    --max-retries 3 \
    --task-timeout 600 \
    --command python \
    --args "manage.py,collectstatic,--noinput" \
    --quiet || warning "Job já existe"

# Executar job
log "  Executando collectstatic..."
gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait
success "Arquivos estáticos coletados!"
echo ""

# RESUMO FINAL
echo ""
echo "========================================"
success "INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "========================================"
echo ""
log "Recursos criados:"
echo "  ✅ Instância Cloud SQL: $INSTANCE_NAME"
echo "  ✅ Banco de dados: $DB_NAME"
echo "  ✅ Usuário: $DB_USER"
echo "  ✅ Imagem Docker: $IMAGE_NAME"
echo "  ✅ Serviço Cloud Run: $SERVICE_NAME"
echo "  ✅ Migrações aplicadas"
echo "  ✅ Arquivos estáticos coletados"
echo ""
log "URLs:"
echo "  🌐 Serviço: $SERVICE_URL"
echo ""
warning "PRÓXIMOS PASSOS:"
echo ""
echo "1. Criar superusuário:"
echo "   gcloud run jobs create create-superuser --image $IMAGE_NAME --region $REGION \\"
echo "     --set-cloudsql-instances $CONNECTION_NAME --set-env-vars $ENV_VARS \\"
echo "     --command python --args 'manage.py,createsuperuser' --interactive"
echo ""
echo "2. Configurar domínio personalizado (opcional):"
echo "   gcloud run domain-mappings create --service $SERVICE_NAME \\"
echo "     --domain monpec.com.br --region $REGION"
echo ""
echo "3. Acessar o sistema:"
echo "   $SERVICE_URL"
echo ""
success "Tudo pronto! 🎉"
echo ""























