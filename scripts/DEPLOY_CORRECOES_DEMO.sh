#!/bin/bash
# 🚀 DEPLOY CORREÇÕES USUÁRIO DEMO - GOOGLE CLOUD RUN
# Script para deploy das correções de validação de usuários demo vs assinantes

set -e  # Parar em caso de erro

# ==========================================
# CONFIGURAÇÕES
# ==========================================
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"
DJANGO_SUPERUSER_PASSWORD="L6171r12@@"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  DEPLOY CORREÇÕES USUÁRIO DEMO${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# ==========================================
# VALIDAÇÕES INICIAIS E PREPARAÇÃO
# ==========================================
echo -e "${BLUE}[1/7] Validando ambiente e preparando diretório...${NC}"

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${YELLOW}⚠️  manage.py não encontrado no diretório atual${NC}"
    echo -e "${BLUE}Tentando encontrar o projeto...${NC}"
    
    # Tentar encontrar o projeto em diretórios comuns
    PROJECT_DIRS=(
        "$HOME/Monpec_GestaoRural"
        "$HOME/monpec-gestao-rural"
        "$HOME/MonPO-Monitor*"
        "$HOME/../Monpec_GestaoRural"
    )
    
    FOUND_DIR=""
    for dir in "${PROJECT_DIRS[@]}"; do
        for path in $dir; do
            if [ -d "$path" ] && [ -f "$path/manage.py" ]; then
                FOUND_DIR="$path"
                break 2
            fi
        done
    done
    
    if [ ! -z "$FOUND_DIR" ]; then
        echo -e "${GREEN}✅ Projeto encontrado em: $FOUND_DIR${NC}"
        cd "$FOUND_DIR"
        echo -e "${GREEN}✅ Diretório alterado para: $(pwd)${NC}"
    else
        echo -e "${RED}❌ ERRO: Projeto Django não encontrado!${NC}"
        echo ""
        echo -e "${YELLOW}Instruções:${NC}"
        echo "1. Se o código já está no Cloud Shell, navegue até o diretório do projeto:"
        echo "   cd /caminho/para/seu/projeto"
        echo ""
        echo "2. Ou faça clone do repositório Git primeiro:"
        echo "   git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git"
        echo "   cd SEU_REPOSITORIO"
        echo ""
        echo "3. Depois execute este script novamente:"
        echo "   bash DEPLOY_CORRECOES_DEMO.sh"
        echo ""
        echo -e "${YELLOW}Diretório atual: $(pwd)${NC}"
        exit 1
    fi
fi

# Verificar arquivos essenciais
if [ ! -f "Dockerfile.prod" ]; then
    echo -e "${RED}❌ ERRO: Dockerfile.prod não encontrado!${NC}"
    echo -e "${YELLOW}Diretório atual: $(pwd)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Arquivos essenciais encontrados em: $(pwd)${NC}"
echo ""

# ==========================================
# CONFIGURAR PROJETO
# ==========================================
echo -e "${BLUE}[2/7] Configurando projeto Google Cloud...${NC}"
gcloud config set project $PROJECT_ID --quiet
echo -e "${GREEN}✅ Projeto configurado: $PROJECT_ID${NC}"
echo ""

# ==========================================
# HABILITAR APIs
# ==========================================
echo -e "${BLUE}[3/7] Habilitando APIs necessárias...${NC}"
gcloud services enable cloudbuild.googleapis.com --quiet 2>/dev/null || true
gcloud services enable run.googleapis.com --quiet 2>/dev/null || true
gcloud services enable sqladmin.googleapis.com --quiet 2>/dev/null || true
gcloud services enable containerregistry.googleapis.com --quiet 2>/dev/null || true
echo -e "${GREEN}✅ APIs habilitadas${NC}"
echo ""

# ==========================================
# CRIAR TAG ÚNICA
# ==========================================
echo -e "${BLUE}[4/7] Criando tag única para a imagem...${NC}"
TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_NAME="gcr.io/$PROJECT_ID/sistema-rural"
IMAGE_TAG="$IMAGE_NAME:v$TIMESTAMP"
IMAGE_LATEST="$IMAGE_NAME:latest"

echo "Tag única: $IMAGE_TAG"
echo "Tag latest: $IMAGE_LATEST"
echo ""

# ==========================================
# BUILD DA IMAGEM
# ==========================================
echo -e "${BLUE}[5/7] Fazendo build da imagem Docker...${NC}"
echo -e "${YELLOW}⚠️  IMPORTANTE: Isso pode levar 15-25 minutos${NC}"
echo -e "${YELLOW}⚠️  Por favor, aguarde e NÃO feche esta janela!${NC}"
echo ""

# Para forçar rebuild sem cache, usamos --substitutions com timestamp
# ou simplesmente fazemos o build normal (o Cloud Build já faz cache inteligente)
gcloud builds submit \
    --tag $IMAGE_TAG \
    --tag $IMAGE_LATEST \
    --timeout=1800s \
    --machine-type=E2_HIGHCPU_8 \
    .

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Tentando build com configuração alternativa...${NC}"
    gcloud builds submit \
        --tag $IMAGE_TAG \
        --tag $IMAGE_LATEST \
        --timeout=1800s \
        .
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ ERRO: Falha no build!${NC}"
        echo "Verifique os logs acima para mais detalhes."
        exit 1
    fi
fi

echo -e "${GREEN}✅ Build concluído${NC}"
echo ""

# ==========================================
# DEPLOY NO CLOUD RUN
# ==========================================
echo -e "${BLUE}[6/7] Fazendo deploy no Cloud Run...${NC}"
echo -e "${YELLOW}⚠️  Isso pode levar 3-10 minutos...${NC}"
echo ""

CLOUD_SQL_CONN="$PROJECT_ID:$REGION:$DB_INSTANCE"

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_LATEST \
    --region=$REGION \
    --platform managed \
    --allow-unauthenticated \
    --add-cloudsql-instances=$CLOUD_SQL_CONN \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONN,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DEMO_USER_PASSWORD=monpec" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --max-instances=10 \
    --min-instances=0 \
    --quiet

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERRO: Falha no deploy!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Deploy concluído${NC}"
echo ""

# ==========================================
# OBTER URL DO SERVIÇO
# ==========================================
echo -e "${BLUE}[7/7] Obtendo URL do serviço...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")

if [ -z "$SERVICE_URL" ]; then
    echo -e "${YELLOW}⚠️  Não foi possível obter a URL automaticamente${NC}"
    echo "Verifique manualmente: gcloud run services describe $SERVICE_NAME --region=$REGION"
else
    echo -e "${GREEN}✅ URL obtida${NC}"
fi
echo ""

# ==========================================
# RESUMO FINAL
# ==========================================
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}✅ Build: SUCESSO${NC}"
echo -e "${GREEN}✅ Deploy: SUCESSO${NC}"
echo ""

if [ ! -z "$SERVICE_URL" ]; then
    echo -e "${CYAN}URL do serviço:${NC} $SERVICE_URL"
    echo ""
    echo -e "${CYAN}Próximos passos:${NC}"
    echo "1. Aguarde 1-2 minutos para o serviço inicializar completamente"
    echo "2. Limpe o cache do navegador (Ctrl+F5)"
    echo "3. Teste o login com um usuário demo"
    echo "4. Verifique que o sistema reconhece corretamente como usuário demo (não assinante)"
    echo ""
fi

echo -e "${CYAN}Ver logs:${NC}"
echo "gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=50"
echo ""

echo -e "${CYAN}Verificar status do serviço:${NC}"
echo "gcloud run services describe $SERVICE_NAME --region=$REGION"
echo ""

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Correções aplicadas:${NC}"
echo -e "${GREEN}  - Usuários demo agora são verificados ANTES de assinantes${NC}"
echo -e "${GREEN}  - Função is_usuario_demo() centralizada${NC}"
echo -e "${GREEN}  - is_usuario_assinante() exclui usuários demo${NC}"
echo -e "${GREEN}  - Middleware e views atualizados${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""


