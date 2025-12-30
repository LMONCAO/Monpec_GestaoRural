#!/bin/bash
# ============================================================================
# DEPLOY COMPLETO AUTOMÁTICO - GOOGLE CLOUD PLATFORM
# ============================================================================
# Este script faz TUDO automaticamente:
# 1. Coleta arquivos estáticos
# 2. Cria usuário admin
# 3. Faz build da imagem Docker
# 4. Faz deploy no Cloud Run
# 5. Configura variáveis de ambiente
# ============================================================================

set -e  # Parar em caso de erro

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parâmetros
PROJETO=${1:-"monpec-sistema-rural"}
SERVICO=${2:-"monpec"}
REGIAO=${3:-"us-central1"}
APENAS_BUILD=${4:-"false"}

echo -e "${CYAN}=========================================="
echo "🚀 DEPLOY AUTOMÁTICO - GOOGLE CLOUD"
echo "==========================================${NC}"
echo ""

# Verificar se gcloud está instalado
echo -e "${CYAN}🔷 Verificando gcloud CLI...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI não está instalado!${NC}"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
echo -e "${GREEN}✅ gcloud CLI encontrado!${NC}"

# Verificar autenticação
echo -e "${CYAN}🔷 Verificando autenticação...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠ Não autenticado. Fazendo login...${NC}"
    gcloud auth login
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Falha na autenticação!${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Autenticado!${NC}"

# Configurar projeto
echo -e "${CYAN}🔷 Configurando projeto: $PROJETO${NC}"
gcloud config set project $PROJETO
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao configurar projeto!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Projeto configurado!${NC}"

# Habilitar APIs necessárias
echo -e "${CYAN}🔷 Habilitando APIs necessárias...${NC}"
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "sqladmin.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "appengine.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo -e "${YELLOW}  Habilitando $api...${NC}"
    gcloud services enable $api --quiet 2>&1 > /dev/null
done
echo -e "${GREEN}✅ APIs habilitadas!${NC}"

# Coletar arquivos estáticos
echo -e "${CYAN}🔷 Coletando arquivos estáticos...${NC}"
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao coletar arquivos estáticos!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Arquivos estáticos coletados!${NC}"

# Verificar se Dockerfile existe
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Dockerfile não encontrado!${NC}"
    echo -e "${YELLOW}Criando Dockerfile básico...${NC}"
    
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expor porta
EXPOSE 8080

# Comando para iniciar
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 sistema_rural.wsgi:application
EOF
    
    echo -e "${GREEN}✅ Dockerfile criado!${NC}"
fi

# Build da imagem
echo -e "${CYAN}🔷 Fazendo build da imagem Docker...${NC}"
IMAGE_TAG="gcr.io/$PROJETO/$SERVICO"
echo -e "${YELLOW}Imagem: $IMAGE_TAG${NC}"

gcloud builds submit --tag $IMAGE_TAG --timeout=20m
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro no build!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Build concluído!${NC}"

if [ "$APENAS_BUILD" = "true" ]; then
    echo ""
    echo -e "${GREEN}🎉 Build concluído! Imagem: $IMAGE_TAG${NC}"
    echo ""
    echo -e "${YELLOW}Para fazer deploy, execute:${NC}"
    echo "  gcloud run deploy $SERVICO --image $IMAGE_TAG --region $REGIAO"
    exit 0
fi

# Deploy no Cloud Run
echo -e "${CYAN}🔷 Fazendo deploy no Cloud Run...${NC}"
echo -e "${YELLOW}Serviço: $SERVICO${NC}"
echo -e "${YELLOW}Região: $REGIAO${NC}"

# Variáveis de ambiente
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,PYTHONUNBUFFERED=1"

# Fazer deploy
gcloud run deploy $SERVICO \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGIAO \
    --allow-unauthenticated \
    --set-env-vars $ENV_VARS \
    --memory=1Gi \
    --cpu=2 \
    --timeout=300 \
    --max-instances=10 \
    --min-instances=1

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro no deploy!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deploy concluído!${NC}"

# Obter URL do serviço
echo -e "${CYAN}🔷 Obtendo URL do serviço...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICO --region=$REGIAO --format="value(status.url)")
echo -e "${GREEN}✅ URL: $SERVICE_URL${NC}"

# Criar usuário admin via Cloud Run Job
echo -e "${CYAN}🔷 Criando usuário admin...${NC}"
JOB_NAME="$SERVICO-admin-setup"

# Criar job temporário
gcloud run jobs create $JOB_NAME \
    --image $IMAGE_TAG \
    --region $REGIAO \
    --set-env-vars $ENV_VARS \
    --command python \
    --args criar_admin_fix.py \
    2>&1 > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${YELLOW}Executando job para criar admin...${NC}"
    gcloud run jobs execute $JOB_NAME --region=$REGIAO --wait
    echo -e "${GREEN}✅ Usuário admin criado!${NC}"
    
    # Limpar job temporário
    gcloud run jobs delete $JOB_NAME --region=$REGIAO --quiet 2>&1 > /dev/null
else
    echo -e "${YELLOW}⚠️  Não foi possível criar job. Execute manualmente:${NC}"
    echo "  python criar_admin_fix.py"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}URL do serviço: $SERVICE_URL${NC}"
echo -e "${YELLOW}Credenciais admin:${NC}"
echo "  Usuário: admin"
echo "  Senha: L6171r12@@"
echo ""
echo -e "${YELLOW}Para ver logs:${NC}"
echo "  gcloud run services logs read $SERVICO --region=$REGIAO"
echo ""










