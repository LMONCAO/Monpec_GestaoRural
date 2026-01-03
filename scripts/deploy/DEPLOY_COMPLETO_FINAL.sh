#!/bin/bash
# 🚀 DEPLOY COMPLETO - SISTEMA MONPEC
# Script completo para fazer deploy do sistema no Google Cloud Run
# Inclui: build, deploy, migrações, collectstatic e configurações

set -e  # Parar em caso de erro

# ========================================
# CONFIGURAÇÕES
# ========================================
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
IMAGE_NAME="gcr.io/$PROJECT_ID/monpec"
DOMAIN="monpec.com.br"
WWW_DOMAIN="www.monpec.com.br"

# IMPORTANTE: Configure estas variáveis antes de executar o deploy!
DB_PASSWORD="${DB_PASSWORD:-Monpec2025!SenhaSegura}"  # Mude isso em produção!
SECRET_KEY="${SECRET_KEY:-}"

# Se SECRET_KEY não estiver configurada, gerar uma nova
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  AVISO: SECRET_KEY não configurado. Gerando uma nova..."
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "django-insecure-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE")
fi

# Variáveis do Mercado Pago (configure via variáveis de ambiente ou Secret Manager)
MERCADOPAGO_ACCESS_TOKEN="${MERCADOPAGO_ACCESS_TOKEN:-}"
MERCADOPAGO_PUBLIC_KEY="${MERCADOPAGO_PUBLIC_KEY:-}"
MERCADOPAGO_WEBHOOK_SECRET="${MERCADOPAGO_WEBHOOK_SECRET:-}"

# Variáveis de Email (opcional)
EMAIL_HOST_USER="${EMAIL_HOST_USER:-}"
EMAIL_HOST_PASSWORD="${EMAIL_HOST_PASSWORD:-}"

# ========================================
# FUNÇÕES AUXILIARES
# ========================================
log() {
    echo "[$(date +'%H:%M:%S')] $1"
}

success() {
    echo "✅ $1"
}

error() {
    echo "❌ $1"
    exit 1
}

warning() {
    echo "⚠️  $1"
}

# ========================================
# INÍCIO DO DEPLOY
# ========================================
echo ""
echo "========================================"
echo "🚀 DEPLOY COMPLETO - SISTEMA MONPEC"
echo "========================================"
echo ""

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    error "gcloud CLI não está instalado! Instale em: https://cloud.google.com/sdk/docs/install"
fi

# Verificar autenticação
log "Verificando autenticação no Google Cloud..."
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1)
if [ -z "$ACCOUNT" ]; then
    error "Você não está autenticado no Google Cloud! Execute: gcloud auth login"
fi
success "Autenticado como: $ACCOUNT"

# Configurar projeto
log "Configurando projeto..."
gcloud config set project "$PROJECT_ID" > /dev/null 2>&1
success "Projeto configurado: $PROJECT_ID"
echo ""

# ========================================
# PARTE 1: HABILITAR APIs
# ========================================
echo "========================================"
log "PARTE 1: HABILITANDO APIs"
echo "========================================"
echo ""

APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "containerregistry.googleapis.com"
    "sqladmin.googleapis.com"
    "sql-component.googleapis.com"
)

for API in "${APIS[@]}"; do
    log "Habilitando $API..."
    gcloud services enable "$API" --quiet > /dev/null 2>&1
done
success "APIs habilitadas!"
echo ""

# ========================================
# PARTE 2: VERIFICAR/CRIAR CLOUD SQL
# ========================================
echo "========================================"
log "PARTE 2: VERIFICANDO CLOUD SQL"
echo "========================================"
echo ""

INSTANCE_EXISTS=false
if gcloud sql instances describe "$INSTANCE_NAME" > /dev/null 2>&1; then
    INSTANCE_EXISTS=true
    success "Instância Cloud SQL já existe: $INSTANCE_NAME"
else
    warning "Instância Cloud SQL não encontrada. Você precisa criá-la manualmente ou usar uma existente."
    echo "Para criar a instância, execute:"
    echo "  gcloud sql instances create $INSTANCE_NAME --database-version=POSTGRES_15 --tier=db-f1-micro --region=$REGION --root-password=$DB_PASSWORD"
    echo ""
    read -p "Deseja continuar mesmo sem a instância? (s/n) " continue
    if [ "$continue" != "s" ] && [ "$continue" != "S" ]; then
        exit 1
    fi
fi

if [ "$INSTANCE_EXISTS" = true ]; then
    CONNECTION_NAME=$(gcloud sql instances describe "$INSTANCE_NAME" --format="value(connectionName)" 2>&1)
    log "Connection name: $CONNECTION_NAME"
    
    # Criar banco de dados
    log "Verificando banco de dados..."
    if gcloud sql databases create "$DB_NAME" --instance="$INSTANCE_NAME" --quiet > /dev/null 2>&1; then
        success "Banco de dados criado: $DB_NAME"
    else
        log "Banco de dados já existe"
    fi
    
    # Criar/atualizar usuário
    log "Verificando usuário do banco..."
    if gcloud sql users create "$DB_USER" --instance="$INSTANCE_NAME" --password="$DB_PASSWORD" --quiet > /dev/null 2>&1; then
        success "Usuário criado: $DB_USER"
    else
        log "Usuário já existe (atualizando senha...)"
        gcloud sql users set-password "$DB_USER" --instance="$INSTANCE_NAME" --password="$DB_PASSWORD" --quiet > /dev/null 2>&1
        success "Senha do usuário atualizada"
    fi
else
    warning "Usando connection name padrão. Configure CLOUD_SQL_CONNECTION_NAME manualmente."
    CONNECTION_NAME="$PROJECT_ID:$REGION:$INSTANCE_NAME"
fi

echo ""

# ========================================
# PARTE 3: BUILD DA IMAGEM DOCKER
# ========================================
echo "========================================"
log "PARTE 3: BUILD DA IMAGEM DOCKER"
echo "========================================"
echo ""

log "Fazendo build da imagem Docker (isso pode levar 5-10 minutos)..."
log "Usando Dockerfile.prod e cloudbuild-config.yaml"

# Verificar se cloudbuild-config.yaml existe
if [ -f "cloudbuild-config.yaml" ]; then
    log "Usando Cloud Build com cloudbuild-config.yaml..."
    gcloud builds submit --config cloudbuild-config.yaml --timeout=600s
else
    log "Fazendo build direto com Docker..."
    gcloud builds submit --tag "$IMAGE_NAME" --timeout=600s
fi

if [ $? -ne 0 ]; then
    error "Erro no build da imagem Docker!"
fi
success "Imagem Docker criada com sucesso!"
echo ""

# ========================================
# PARTE 4: CONFIGURAR VARIÁVEIS DE AMBIENTE
# ========================================
echo "========================================"
log "PARTE 4: CONFIGURANDO VARIÁVEIS DE AMBIENTE"
echo "========================================"
echo ""

# Construir string de variáveis de ambiente
ENV_VARS=(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"
    "SECRET_KEY=$SECRET_KEY"
    "DEBUG=False"
    "DB_NAME=$DB_NAME"
    "DB_USER=$DB_USER"
    "DB_PASSWORD=$DB_PASSWORD"
    "CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME"
    "PORT=8080"
    "PYTHONUNBUFFERED=1"
    "SITE_URL=https://$DOMAIN"
    "MERCADOPAGO_SUCCESS_URL=https://$DOMAIN/assinaturas/sucesso/"
    "MERCADOPAGO_CANCEL_URL=https://$DOMAIN/assinaturas/cancelado/"
    "PAYMENT_GATEWAY_DEFAULT=mercadopago"
)

# Adicionar variáveis do Mercado Pago se configuradas
if [ -n "$MERCADOPAGO_ACCESS_TOKEN" ]; then
    ENV_VARS+=("MERCADOPAGO_ACCESS_TOKEN=$MERCADOPAGO_ACCESS_TOKEN")
fi
if [ -n "$MERCADOPAGO_PUBLIC_KEY" ]; then
    ENV_VARS+=("MERCADOPAGO_PUBLIC_KEY=$MERCADOPAGO_PUBLIC_KEY")
fi
if [ -n "$MERCADOPAGO_WEBHOOK_SECRET" ]; then
    ENV_VARS+=("MERCADOPAGO_WEBHOOK_SECRET=$MERCADOPAGO_WEBHOOK_SECRET")
fi

# Adicionar variáveis de email se configuradas
if [ -n "$EMAIL_HOST_USER" ]; then
    ENV_VARS+=("EMAIL_HOST_USER=$EMAIL_HOST_USER")
    ENV_VARS+=("EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
    ENV_VARS+=("EMAIL_HOST=smtp.gmail.com")
    ENV_VARS+=("EMAIL_PORT=587")
    ENV_VARS+=("EMAIL_USE_TLS=True")
    ENV_VARS+=("DEFAULT_FROM_EMAIL=noreply@$DOMAIN")
fi
if [ -n "$EMAIL_HOST_PASSWORD" ]; then
    ENV_VARS+=("EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD")
fi

ENV_VARS_STRING=$(IFS=','; echo "${ENV_VARS[*]}")

log "Variáveis de ambiente configuradas:"
for var in "${ENV_VARS[@]}"; do
    if [[ "$var" =~ (PASSWORD|SECRET|TOKEN) ]]; then
        echo "  ${var%%=*}=***"
    else
        echo "  $var"
    fi
done
echo ""

# ========================================
# PARTE 5: DEPLOY NO CLOUD RUN
# ========================================
echo "========================================"
log "PARTE 5: DEPLOY NO CLOUD RUN"
echo "========================================"
echo ""

log "Fazendo deploy no Cloud Run..."

DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars $ENV_VARS_STRING \
    --memory 2Gi \
    --cpu 2 \
    --timeout 600 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080"

# Adicionar conexão Cloud SQL se disponível
if [ "$INSTANCE_EXISTS" = true ]; then
    DEPLOY_CMD="$DEPLOY_CMD --add-cloudsql-instances $CONNECTION_NAME"
fi

eval $DEPLOY_CMD

if [ $? -ne 0 ]; then
    error "Erro no deploy do Cloud Run!"
fi

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1)
success "Deploy no Cloud Run concluído!"
log "URL do serviço: $SERVICE_URL"
echo ""

# ========================================
# PARTE 6: APLICAR MIGRAÇÕES
# ========================================
echo "========================================"
log "PARTE 6: APLICANDO MIGRAÇÕES"
echo "========================================"
echo ""

JOB_NAME="migrate-monpec"
log "Criando/atualizando job de migração..."

JOB_CMD="gcloud run jobs create $JOB_NAME \
    --image $IMAGE_NAME:latest \
    --region $REGION \
    --set-env-vars $ENV_VARS_STRING \
    --memory 2Gi \
    --cpu 1 \
    --max-retries 3 \
    --task-timeout 600 \
    --command python \
    --args manage.py,migrate,--noinput"

if [ "$INSTANCE_EXISTS" = true ]; then
    JOB_CMD="$JOB_CMD --set-cloudsql-instances $CONNECTION_NAME"
fi

if eval $JOB_CMD --quiet > /dev/null 2>&1; then
    success "Job de migração criado!"
else
    log "Job já existe, atualizando..."
    JOB_CMD=$(echo "$JOB_CMD" | sed 's/ create / update /')
    eval $JOB_CMD --quiet > /dev/null 2>&1
    success "Job de migração atualizado!"
fi

log "Executando migrações (aguarde...)"
gcloud run jobs execute $JOB_NAME --region $REGION --wait > /dev/null 2>&1
if [ $? -eq 0 ]; then
    success "Migrações aplicadas com sucesso!"
else
    warning "Aviso: Pode ter havido algum problema nas migrações. Verifique os logs."
fi
echo ""

# ========================================
# PARTE 7: COLETAR ARQUIVOS ESTÁTICOS
# ========================================
echo "========================================"
log "PARTE 7: COLETANDO ARQUIVOS ESTÁTICOS"
echo "========================================"
echo ""

STATIC_JOB_NAME="collectstatic-monpec"
log "Criando/atualizando job de collectstatic..."

STATIC_JOB_CMD="gcloud run jobs create $STATIC_JOB_NAME \
    --image $IMAGE_NAME:latest \
    --region $REGION \
    --set-env-vars $ENV_VARS_STRING \
    --memory 2Gi \
    --cpu 1 \
    --max-retries 3 \
    --task-timeout 600 \
    --command python \
    --args manage.py,collectstatic,--noinput"

if [ "$INSTANCE_EXISTS" = true ]; then
    STATIC_JOB_CMD="$STATIC_JOB_CMD --set-cloudsql-instances $CONNECTION_NAME"
fi

if eval $STATIC_JOB_CMD --quiet > /dev/null 2>&1; then
    success "Job de collectstatic criado!"
else
    log "Job já existe, atualizando..."
    STATIC_JOB_CMD=$(echo "$STATIC_JOB_CMD" | sed 's/ create / update /')
    eval $STATIC_JOB_CMD --quiet > /dev/null 2>&1
    success "Job de collectstatic atualizado!"
fi

log "Coletando arquivos estáticos (aguarde...)"
gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait > /dev/null 2>&1
if [ $? -eq 0 ]; then
    success "Arquivos estáticos coletados com sucesso!"
else
    warning "Aviso: Pode ter havido algum problema no collectstatic. Verifique os logs."
fi
echo ""

# ========================================
# PARTE 8: CONFIGURAR DOMÍNIO (OPCIONAL)
# ========================================
echo "========================================"
log "PARTE 8: CONFIGURAÇÃO DE DOMÍNIO"
echo "========================================"
echo ""

read -p "Deseja configurar o domínio personalizado? (s/n) " configureDomain
if [ "$configureDomain" = "s" ] || [ "$configureDomain" = "S" ]; then
    log "Criando domain mapping para $DOMAIN..."
    if gcloud run domain-mappings create --service $SERVICE_NAME --domain $DOMAIN --region $REGION --quiet > /dev/null 2>&1; then
        success "Domain mapping criado para $DOMAIN"
    else
        log "Domain mapping já existe para $DOMAIN"
    fi

    log "Criando domain mapping para $WWW_DOMAIN..."
    if gcloud run domain-mappings create --service $SERVICE_NAME --domain $WWW_DOMAIN --region $REGION --quiet > /dev/null 2>&1; then
        success "Domain mapping criado para $WWW_DOMAIN"
    else
        log "Domain mapping já existe para $WWW_DOMAIN"
    fi

    log "Obtendo informações de DNS..."
    DNS_RECORDS=$(gcloud run domain-mappings describe $DOMAIN --region $REGION --format="value(status.resourceRecords)" 2>&1 || echo "")
    if [ -n "$DNS_RECORDS" ]; then
        success "Domain mappings configurados!"
        warning "IMPORTANTE: Configure os registros DNS no seu provedor de domínio"
        gcloud run domain-mappings describe $DOMAIN --region $REGION --format="table(status.resourceRecords)"
    else
        warning "Domain mappings criados, mas pode levar alguns minutos para propagar"
    fi
else
    log "Pulando configuração de domínio"
fi
echo ""

# ========================================
# PARTE 9: VERIFICAÇÃO FINAL
# ========================================
echo "========================================"
log "PARTE 9: VERIFICAÇÃO FINAL"
echo "========================================"
echo ""

log "Verificando status do serviço..."
SERVICE_STATUS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.conditions[0].status)" 2>&1)
if [ "$SERVICE_STATUS" = "True" ]; then
    success "Serviço está ativo e funcionando!"
else
    warning "Serviço pode estar inicializando..."
fi

log "Testando conectividade..."
sleep 5
if curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" | grep -qE "^(200|301|302)$"; then
    success "Serviço respondendo corretamente"
else
    warning "Não foi possível testar conectividade agora (serviço pode estar inicializando)"
    log "Tente acessar: $SERVICE_URL"
fi

# ========================================
# RESUMO FINAL
# ========================================
echo ""
echo "========================================"
success "✅ DEPLOY COMPLETO CONCLUÍDO!"
echo "========================================"
echo ""
echo "📋 RECURSOS CRIADOS/ATUALIZADOS:"
if [ "$INSTANCE_EXISTS" = true ]; then
    echo "  ✅ Instância Cloud SQL: $INSTANCE_NAME"
    echo "  ✅ Banco de dados: $DB_NAME"
fi
echo "  ✅ Serviço Cloud Run: $SERVICE_NAME"
echo "  ✅ Migrações aplicadas"
echo "  ✅ Arquivos estáticos coletados"
echo ""
echo "🌐 URLs:"
echo "  • Cloud Run: $SERVICE_URL"
if [ "$configureDomain" = "s" ] || [ "$configureDomain" = "S" ]; then
    echo "  • Domínio: https://$DOMAIN (após configurar DNS)"
    echo "  • WWW: https://$WWW_DOMAIN (após configurar DNS)"
fi
echo ""
echo "📝 PRÓXIMOS PASSOS:"
echo ""
if [ "$configureDomain" = "s" ] || [ "$configureDomain" = "S" ]; then
    echo "1. Configure os registros DNS no seu provedor de domínio"
    echo "   (execute: gcloud run domain-mappings describe $DOMAIN --region $REGION)"
    echo ""
    echo "2. Aguarde a propagação DNS (geralmente 5-30 minutos)"
    echo ""
fi
echo "3. Acesse o sistema:"
echo "   $SERVICE_URL"
echo ""
echo "4. Para criar superusuário, execute:"
echo "   gcloud run jobs create create-superuser --image $IMAGE_NAME:latest --region $REGION --set-cloudsql-instances $CONNECTION_NAME --set-env-vars $ENV_VARS_STRING --command python --args 'manage.py,createsuperuser' --interactive"
echo ""
if [ -z "$MERCADOPAGO_ACCESS_TOKEN" ]; then
    warning "⚠️  IMPORTANTE: Configure as variáveis do Mercado Pago no Cloud Run:"
    echo "   gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars MERCADOPAGO_ACCESS_TOKEN=SEU_TOKEN,MERCADOPAGO_PUBLIC_KEY=SUA_KEY"
    echo ""
fi
success "🎉 Tudo pronto! Sistema disponível em: $SERVICE_URL"
echo ""









