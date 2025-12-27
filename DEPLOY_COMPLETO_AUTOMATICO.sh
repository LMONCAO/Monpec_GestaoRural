#!/bin/bash
# 🚀 DEPLOY COMPLETO AUTOMÁTICO - MONPEC.COM.BR
# Executa limpeza, instalação, configuração de domínio e verificação
# Projeto: monpec-sistema-rural

set -e  # Parar em caso de erro

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
IMAGE_NAME="gcr.io/$PROJECT_ID/monpec"
DOMAIN="monpec.com.br"
WWW_DOMAIN="www.monpec.com.br"

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

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

echo ""
echo "========================================"
echo "🚀 DEPLOY COMPLETO AUTOMÁTICO - MONPEC"
echo "========================================"
echo ""
info "Este script vai:"
echo "  1. Limpar recursos antigos do GCP"
echo "  2. Criar instância Cloud SQL"
echo "  3. Fazer build e deploy no Cloud Run"
echo "  4. Configurar domínio monpec.com.br"
echo "  5. Verificar se tudo está funcionando"
echo ""

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    error "gcloud CLI não está instalado!"
    exit 1
fi

# Verificar projeto
log "Verificando projeto..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    warning "Projeto atual: $CURRENT_PROJECT"
    gcloud config set project $PROJECT_ID
    success "Projeto configurado para: $PROJECT_ID"
else
    success "Projeto correto: $PROJECT_ID"
fi
echo ""

# Solicitar credenciais
warning "Você precisará fornecer:"
echo "  1. Senha do banco de dados (mínimo 8 caracteres)"
echo "  2. SECRET_KEY do Django (ou deixar gerar automaticamente)"
echo ""

read -sp "Digite a senha do banco de dados: " DB_PASSWORD
echo ""
if [ ${#DB_PASSWORD} -lt 8 ]; then
    error "Senha deve ter no mínimo 8 caracteres!"
    exit 1
fi

read -p "Deseja fornecer SECRET_KEY? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    read -sp "Digite a SECRET_KEY: " SECRET_KEY
    echo ""
else
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 50)
    success "SECRET_KEY gerada automaticamente"
fi
echo ""

# PARTE 1: LIMPEZA
echo ""
echo "========================================"
log "PARTE 1: LIMPEZA DE RECURSOS"
echo "========================================"
echo ""

# Deletar serviço Cloud Run
log "Deletando serviço Cloud Run..."
gcloud run services delete $SERVICE_NAME --region $REGION --quiet 2>/dev/null || warning "Serviço não encontrado"

# Deletar jobs
log "Deletando jobs..."
gcloud run jobs list --region $REGION --format="value(name)" 2>/dev/null | grep -i monpec | while read JOB; do
    gcloud run jobs delete $JOB --region $REGION --quiet 2>/dev/null || true
done

# Verificar e deletar instância Cloud SQL
log "Verificando instância Cloud SQL..."
if gcloud sql instances describe $INSTANCE_NAME &>/dev/null; then
    warning "Instância Cloud SQL existe. Deseja deletar? (s/n)"
    read -p "" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        gcloud sql instances delete $INSTANCE_NAME --quiet
        success "Instância deletada!"
        log "Aguardando 30 segundos para garantir exclusão..."
        sleep 30
    fi
fi

success "Limpeza concluída!"
echo ""

# PARTE 2: INSTALAÇÃO
echo ""
echo "========================================"
log "PARTE 2: INSTALAÇÃO DO ZERO"
echo "========================================"
echo ""

# Habilitar APIs
log "Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable sql-component.googleapis.com --quiet
success "APIs habilitadas!"

# Criar instância Cloud SQL
log "Criando instância Cloud SQL PostgreSQL 15..."
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

# Obter connection name
CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
log "Connection name: $CONNECTION_NAME"

# Criar banco e usuário
log "Criando banco de dados e usuário..."
gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --quiet || warning "Banco já existe"
gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet || warning "Usuário já existe"
success "Banco e usuário criados!"

# Build da imagem
log "Fazendo build da imagem Docker (isso pode levar alguns minutos)..."
gcloud builds submit --tag $IMAGE_NAME --timeout=600s
success "Imagem Docker criada!"

# Deploy no Cloud Run
log "Fazendo deploy no Cloud Run..."
ENV_VARS="DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

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

# Obter URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
log "URL do serviço: $SERVICE_URL"

# Aplicar migrações
log "Aplicando migrações..."
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

gcloud run jobs execute $JOB_NAME --region $REGION --wait
success "Migrações aplicadas!"

# Coletar estáticos
log "Coletando arquivos estáticos..."
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

gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait
success "Arquivos estáticos coletados!"

# PARTE 3: CONFIGURAR DOMÍNIO
echo ""
echo "========================================"
log "PARTE 3: CONFIGURAÇÃO DE DOMÍNIO"
echo "========================================"
echo ""

log "Criando domain mapping para $DOMAIN..."
gcloud run domain-mappings create \
    --service $SERVICE_NAME \
    --domain $DOMAIN \
    --region $REGION \
    --quiet || warning "Domain mapping já existe"

log "Criando domain mapping para $WWW_DOMAIN..."
gcloud run domain-mappings create \
    --service $SERVICE_NAME \
    --domain $WWW_DOMAIN \
    --region $REGION \
    --quiet || warning "Domain mapping já existe"

# Obter informações de DNS
log "Obtendo informações de DNS..."
DOMAIN_MAPPING=$(gcloud run domain-mappings describe $DOMAIN --region $REGION --format="value(status.resourceRecords)" 2>/dev/null || echo "")

if [ -n "$DOMAIN_MAPPING" ]; then
    success "Domain mappings criados!"
    warning "IMPORTANTE: Configure os registros DNS no seu provedor de domínio:"
    echo ""
    gcloud run domain-mappings describe $DOMAIN --region $REGION --format="table(status.resourceRecords)"
    echo ""
else
    warning "Domain mappings criados, mas pode levar alguns minutos para propagar"
fi

# PARTE 4: VERIFICAÇÃO
echo ""
echo "========================================"
log "PARTE 4: VERIFICAÇÃO"
echo "========================================"
echo ""

log "Verificando status do serviço..."
SERVICE_STATUS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)" 2>/dev/null)
if [ "$SERVICE_STATUS" = "True" ]; then
    success "Serviço está ativo!"
else
    error "Serviço não está ativo!"
fi

log "Testando conectividade..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$SERVICE_URL" 2>/dev/null || echo "000")
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
    success "Serviço respondendo (HTTP $HTTP_STATUS)"
else
    warning "Serviço retornou HTTP $HTTP_STATUS (pode estar inicializando)"
fi

# RESUMO FINAL
echo ""
echo "========================================"
success "DEPLOY COMPLETO CONCLUÍDO!"
echo "========================================"
echo ""
log "Recursos criados:"
echo "  ✅ Instância Cloud SQL: $INSTANCE_NAME"
echo "  ✅ Banco de dados: $DB_NAME"
echo "  ✅ Serviço Cloud Run: $SERVICE_NAME"
echo "  ✅ Domain mappings: $DOMAIN e $WWW_DOMAIN"
echo ""
log "URLs:"
echo "  🌐 Cloud Run: $SERVICE_URL"
echo "  🌐 Domínio: https://$DOMAIN (pode levar alguns minutos para propagar)"
echo "  🌐 WWW: https://$WWW_DOMAIN (pode levar alguns minutos para propagar)"
echo ""
warning "PRÓXIMOS PASSOS:"
echo ""
echo "1. Configure os registros DNS no seu provedor de domínio"
echo "   (os registros foram exibidos acima)"
echo ""
echo "2. Aguarde a propagação DNS (pode levar até 48 horas, geralmente 5-30 minutos)"
echo ""
echo "3. Criar superusuário:"
echo "   gcloud run jobs create create-superuser \\"
echo "     --image $IMAGE_NAME --region $REGION \\"
echo "     --set-cloudsql-instances $CONNECTION_NAME \\"
echo "     --set-env-vars $ENV_VARS \\"
echo "     --command python --args 'manage.py,createsuperuser' --interactive"
echo ""
echo "4. Acessar o sistema:"
echo "   $SERVICE_URL (funciona imediatamente)"
echo "   https://$DOMAIN (após configurar DNS)"
echo ""
success "Tudo pronto! 🎉"
echo ""
















