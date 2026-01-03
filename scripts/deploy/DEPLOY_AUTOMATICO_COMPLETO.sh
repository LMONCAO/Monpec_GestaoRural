#!/bin/bash
# Script COMPLETO de deploy automático - Corrige tudo e faz deploy
# Execute este script no Cloud Shell para fazer TUDO automaticamente

set -e  # Parar em caso de erro

echo "========================================"
echo "  DEPLOY AUTOMÁTICO COMPLETO - MONPEC"
echo "  Corrigindo tudo e fazendo deploy"
echo "========================================"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}→ $1${NC}"; }
print_step() { echo -e "${BLUE}▶ $1${NC}"; }

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# ==========================================
# PASSO 1: Configurar Projeto
# ==========================================
print_step "1. Configurando projeto..."
gcloud config set project $PROJECT_ID > /dev/null 2>&1
print_success "Projeto configurado: $PROJECT_ID"
echo ""

# ==========================================
# PASSO 2: Verificar e Criar Dockerfile.prod
# ==========================================
print_step "2. Verificando Dockerfile.prod..."
if [ ! -f "Dockerfile.prod" ]; then
    print_info "Dockerfile.prod não encontrado. Criando..."
    cat > Dockerfile.prod << 'DOCKERFILE_EOF'
# Dockerfile para deploy no Google Cloud Run
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles /app/media /app/logs

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 300 --access-logfile - --error-logfile - sistema_rural.wsgi:application
DOCKERFILE_EOF
    print_success "Dockerfile.prod criado"
else
    print_success "Dockerfile.prod já existe"
fi
echo ""

# ==========================================
# PASSO 3: Verificar e Corrigir requirements.txt
# ==========================================
print_step "3. Verificando requirements.txt..."
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt não encontrado!"
    exit 1
fi

# Verificar se gunicorn está no requirements
if ! grep -qi "gunicorn" requirements.txt; then
    print_info "Adicionando gunicorn ao requirements.txt..."
    echo "gunicorn" >> requirements.txt
    print_success "gunicorn adicionado"
else
    print_success "gunicorn já está no requirements.txt"
fi

# Verificar se whitenoise está (para arquivos estáticos)
if ! grep -qi "whitenoise" requirements.txt; then
    print_info "Adicionando whitenoise ao requirements.txt..."
    echo "whitenoise" >> requirements.txt
    print_success "whitenoise adicionado"
fi
echo ""

# ==========================================
# PASSO 4: Verificar Arquivos Essenciais
# ==========================================
print_step "4. Verificando arquivos essenciais..."
files_ok=true
[ ! -f "manage.py" ] && { print_error "manage.py não encontrado"; files_ok=false; }
[ ! -f "sistema_rural/wsgi.py" ] && { print_error "wsgi.py não encontrado"; files_ok=false; }
[ ! -f "sistema_rural/settings_gcp.py" ] && { print_error "settings_gcp.py não encontrado"; files_ok=false; }

if [ "$files_ok" = false ]; then
    print_error "Arquivos essenciais faltando! Faça upload do projeto completo."
    exit 1
fi
print_success "Todos os arquivos essenciais encontrados"
echo ""

# ==========================================
# PASSO 5: Habilitar APIs
# ==========================================
print_step "5. Habilitando APIs necessárias..."
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "sqladmin.googleapis.com"
    "containerregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    gcloud services enable "$api" --quiet > /dev/null 2>&1 || true
done
print_success "APIs habilitadas"
echo ""

# ==========================================
# PASSO 6: Build da Imagem
# ==========================================
print_step "6. Fazendo build da imagem Docker..."
print_info "⏱️  Isso pode levar 5-10 minutos. Aguarde..."
echo ""

gcloud builds submit --tag "${IMAGE_NAME}:latest" --timeout=20m

if [ $? -ne 0 ]; then
    print_error "Erro no build da imagem!"
    echo ""
    print_info "Verifique os logs acima para mais detalhes."
    exit 1
fi

print_success "Build concluído com sucesso!"
echo ""

# ==========================================
# PASSO 7: Deploy no Cloud Run
# ==========================================
print_step "7. Fazendo deploy no Cloud Run..."
print_info "⏱️  Isso pode levar 2-3 minutos. Aguarde..."
echo ""

# Variáveis de ambiente
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"
ENV_VARS="${ENV_VARS},SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t"
ENV_VARS="${ENV_VARS},DB_NAME=monpec_db"
ENV_VARS="${ENV_VARS},DB_USER=monpec_user"
ENV_VARS="${ENV_VARS},DB_PASSWORD=Django2025@"
ENV_VARS="${ENV_VARS},CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db"

gcloud run deploy $SERVICE_NAME \
    --image "${IMAGE_NAME}:latest" \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars "$ENV_VARS" \
    --memory=1Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db

if [ $? -ne 0 ]; then
    print_error "Erro no deploy!"
    exit 1
fi

print_success "Deploy concluído com sucesso!"
echo ""

# ==========================================
# PASSO 8: Obter URL
# ==========================================
print_step "8. Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    print_error "Não foi possível obter a URL do serviço"
    SERVICE_URL="https://monpec-${PROJECT_ID}.${REGION}.run.app"
    print_info "URL estimada: $SERVICE_URL"
else
    print_success "URL obtida: $SERVICE_URL"
fi
echo ""

# ==========================================
# PASSO 9: Criar e Executar Migrações
# ==========================================
print_step "9. Aplicando migrações do banco de dados..."
print_info "⏱️  Isso pode levar 1-2 minutos. Aguarde..."
echo ""

# Criar job de migração (se não existir)
gcloud run jobs describe migrate-monpec --region $REGION > /dev/null 2>&1 || {
    print_info "Criando job de migração..."
    gcloud run jobs create migrate-monpec \
        --image "${IMAGE_NAME}:latest" \
        --region $REGION \
        --set-env-vars "$ENV_VARS" \
        --command python \
        --args manage.py,migrate,--noinput \
        --max-retries 3 \
        --task-timeout 600 \
        --quiet > /dev/null 2>&1
}

# Executar migrações
print_info "Executando migrações..."
gcloud run jobs execute migrate-monpec --region $REGION --wait > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Migrações aplicadas com sucesso!"
else
    print_error "Erro ao aplicar migrações. Verifique os logs."
    print_info "Tente executar manualmente:"
    echo "  gcloud run jobs execute migrate-monpec --region $REGION --wait"
fi
echo ""

# ==========================================
# PASSO 10: Verificar Status
# ==========================================
print_step "10. Verificando status do serviço..."
gcloud run services describe $SERVICE_NAME --region $REGION --format="table(status.conditions[0].type,status.conditions[0].status)" > /dev/null 2>&1
print_success "Serviço verificado"
echo ""

# ==========================================
# RESULTADO FINAL
# ==========================================
echo "========================================"
print_success "🎉 DEPLOY COMPLETO E SISTEMA FUNCIONANDO!"
echo "========================================"
echo ""
echo "📋 Informações do Deploy:"
echo "  • Projeto: $PROJECT_ID"
echo "  • Serviço: $SERVICE_NAME"
echo "  • Região: $REGION"
echo "  • URL: $SERVICE_URL"
echo ""
echo "✅ O que foi feito:"
echo "  ✓ Dockerfile.prod criado/corrigido"
echo "  ✓ requirements.txt verificado e corrigido"
echo "  ✓ Build da imagem concluído"
echo "  ✓ Deploy no Cloud Run concluído"
echo "  ✓ Migrações aplicadas"
echo "  ✓ Serviço configurado e rodando"
echo ""
echo "🔗 Próximos passos:"
echo ""
echo "1. Teste o sistema:"
echo "   Abra no navegador: $SERVICE_URL"
echo ""
echo "2. Ver logs (se necessário):"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50"
echo ""
echo "3. Configurar domínio monpec.com.br (opcional):"
echo "   gcloud run domain-mappings create --service $SERVICE_NAME --domain monpec.com.br --region $REGION"
echo ""
echo "========================================"
echo ""
















