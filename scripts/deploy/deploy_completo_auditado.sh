#!/bin/bash
# Script de Deploy Completo com Auditoria e Validações
# Execute: bash deploy_completo_auditado.sh

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

# Funções de log
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_step() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

# Header
clear
log_step "🚀 DEPLOY COMPLETO MONPEC - COM AUDITORIA"

# ==========================================
# ETAPA 1: AUDITORIA PRÉ-DEPLOY
# ==========================================
log_step "ETAPA 1: AUDITORIA PRÉ-DEPLOY"

if [ -f "auditoria_pre_deploy.sh" ]; then
    log_info "Executando auditoria pré-deploy..."
    bash auditoria_pre_deploy.sh
    if [ $? -ne 0 ]; then
        log_error "Auditoria falhou! Corrija os erros antes de continuar."
        exit 1
    fi
else
    log_warning "Script de auditoria não encontrado, pulando..."
fi

# ==========================================
# ETAPA 2: VERIFICAÇÕES DO GOOGLE CLOUD
# ==========================================
log_step "ETAPA 2: VERIFICAÇÕES DO GOOGLE CLOUD"

# Verificar autenticação
log_info "Verificando autenticação..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    log_error "Não autenticado no Google Cloud!"
    log_info "Execute: gcloud auth login"
    exit 1
fi
log_success "Autenticado no Google Cloud"

# Configurar projeto
log_info "Configurando projeto: $PROJECT_ID"
gcloud config set project $PROJECT_ID || {
    log_error "Erro ao configurar projeto!"
    exit 1
}
log_success "Projeto configurado"

# Verificar APIs habilitadas
log_info "Verificando APIs necessárias..."
APIS=("cloudbuild.googleapis.com" "run.googleapis.com" "sqladmin.googleapis.com")
for api in "${APIS[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        log_success "API $api habilitada"
    else
        log_warning "API $api não habilitada, habilitando..."
        gcloud services enable $api --quiet || log_warning "Não foi possível habilitar $api"
    fi
done

# Verificar instância Cloud SQL
log_info "Verificando instância Cloud SQL..."
if gcloud sql instances describe monpec-db --format="value(name)" 2>/dev/null | grep -q "monpec-db"; then
    log_success "Instância monpec-db encontrada"
else
    log_error "Instância monpec-db não encontrada!"
    exit 1
fi

# Verificar usuário do banco
log_info "Verificando usuário do banco..."
if gcloud sql users list --instance=monpec-db --format="value(name)" 2>/dev/null | grep -q "monpec_user"; then
    log_success "Usuário monpec_user existe"
else
    log_warning "Usuário monpec_user não encontrado, criando..."
    gcloud sql users create monpec_user --instance=monpec-db --password="$DB_PASSWORD" || {
        log_error "Não foi possível criar usuário"
        exit 1
    }
fi

# ==========================================
# ETAPA 3: PREPARAÇÃO DO CÓDIGO
# ==========================================
log_step "ETAPA 3: PREPARAÇÃO DO CÓDIGO"

# Garantir openpyxl no requirements
log_info "Verificando requirements_producao.txt..."
if [ ! -f "requirements_producao.txt" ]; then
    log_error "requirements_producao.txt não encontrado!"
    exit 1
fi

if ! grep -q "^openpyxl" requirements_producao.txt; then
    log_warning "openpyxl não encontrado, adicionando..."
    echo "openpyxl>=3.1.5" >> requirements_producao.txt
    log_success "openpyxl adicionado"
else
    log_success "openpyxl já está no requirements"
fi

# Verificar Dockerfile
log_info "Verificando Dockerfile.prod..."
if [ ! -f "Dockerfile.prod" ] || [ ! -s "Dockerfile.prod" ]; then
    log_error "Dockerfile.prod não encontrado ou está vazio!"
    exit 1
fi
log_success "Dockerfile.prod OK"

# ==========================================
# ETAPA 4: BUILD DA IMAGEM
# ==========================================
log_step "ETAPA 4: BUILD DA IMAGEM DOCKER"

TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
LATEST_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

log_info "Tag da imagem: $IMAGE_TAG"
log_info "Isso pode levar 5-10 minutos..."
echo ""

gcloud builds submit --tag $IMAGE_TAG --timeout=20m || {
    log_error "Build falhou!"
    log_info "Verifique os logs acima para mais detalhes"
    exit 1
}

log_success "Build concluído com sucesso!"

# Marcar como latest
log_info "Marcando como latest..."
gcloud container images add-tag $IMAGE_TAG $LATEST_TAG --quiet || log_warning "Não foi possível marcar como latest"

# ==========================================
# ETAPA 5: DEPLOY NO CLOUD RUN
# ==========================================
log_step "ETAPA 5: DEPLOY NO CLOUD RUN"

log_info "Preparando variáveis de ambiente..."
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

log_info "Isso pode levar 2-5 minutos..."
echo ""

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances="$PROJECT_ID:$REGION:monpec-db" \
    --set-env-vars "$ENV_VARS" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=80 \
    --port=8080 || {
    log_error "Deploy falhou!"
    log_info "Verifique os logs acima para mais detalhes"
    exit 1
}

log_success "Deploy concluído com sucesso!"

# ==========================================
# ETAPA 6: VERIFICAÇÕES PÓS-DEPLOY
# ==========================================
log_step "ETAPA 6: VERIFICAÇÕES PÓS-DEPLOY"

# Obter URL
log_info "Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    log_error "Não foi possível obter URL do serviço"
else
    log_success "URL obtida: $SERVICE_URL"
fi

# Aguardar inicialização
log_info "Aguardando 30 segundos para inicialização..."
sleep 30

# Verificar saúde do serviço
log_info "Verificando saúde do serviço..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    log_success "Serviço respondendo (HTTP $HTTP_CODE)"
else
    log_warning "Serviço retornou HTTP $HTTP_CODE (pode estar inicializando)"
fi

# Verificar logs recentes
log_info "Verificando logs recentes..."
ERROR_COUNT=$(gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=5 --format="value(severity)" 2>/dev/null | wc -l)

if [ "$ERROR_COUNT" -gt 0 ]; then
    log_warning "Encontrados $ERROR_COUNT erros nos logs recentes"
    log_info "Verifique os logs: gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR\" --limit=10"
else
    log_success "Nenhum erro crítico nos logs recentes"
fi

# ==========================================
# ETAPA 7: GARANTIR ADMIN
# ==========================================
log_step "ETAPA 7: GARANTINDO USUÁRIO ADMIN"

log_info "Criando/verificando usuário admin..."
gcloud run jobs execute garantir-admin \
    --region=$REGION \
    --args python,manage.py,garantir_admin \
    2>/dev/null || {
    log_warning "Job garantir-admin não existe, criando admin via shell..."
    gcloud run jobs execute criar-admin \
        --region=$REGION \
        --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();user,created=User.objects.get_or_create(username='admin',defaults={'email':'admin@monpec.com.br','is_staff':True,'is_superuser':True,'is_active':True});user.set_password('L6171r12@@');user.save();auth_test=authenticate(username='admin',password='L6171r12@@');print('✅ Admin criado!' if auth_test else '❌ Falha')" \
        2>/dev/null || log_warning "Não foi possível criar admin automaticamente"
}

# ==========================================
# RESUMO FINAL
# ==========================================
log_step "✅✅✅ DEPLOY CONCLUÍDO! ✅✅✅"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📋 INFORMAÇÕES DO DEPLOY${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${CYAN}🔗 URL do Serviço:${NC}"
echo "   $SERVICE_URL"
echo ""
echo -e "${CYAN}📋 Credenciais para Login:${NC}"
echo "   Username: admin"
echo "   Senha: L6171r12@@"
echo ""
echo -e "${CYAN}⏱️  Próximos Passos:${NC}"
echo "   1. Aguarde 1-2 minutos para inicialização completa"
echo "   2. Acesse: $SERVICE_URL"
echo "   3. Faça login com as credenciais acima"
echo ""
echo -e "${CYAN}🔍 Verificar Logs:${NC}"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=20"
echo ""
echo -e "${GREEN}========================================${NC}"
echo ""


