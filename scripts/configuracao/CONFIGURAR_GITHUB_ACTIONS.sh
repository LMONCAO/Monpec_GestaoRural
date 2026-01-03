#!/bin/bash
# 🚀 Script Completo para Configurar GitHub Actions → Google Cloud (Linux/Mac)
# Este script automatiza a configuração completa do deploy automático

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_ACCOUNT_NAME="github-actions-deploy"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="github-actions-key.json"

echo ""
echo "========================================"
echo -e "${CYAN}🚀 CONFIGURAR GITHUB ACTIONS - GCP${NC}"
echo "========================================"
echo ""

# Verificar gcloud
echo -e "${CYAN}Verificando gcloud CLI...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI não encontrado! Instale em: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi
echo -e "${GREEN}✅ gcloud CLI encontrado!${NC}"

# Verificar autenticação
echo -e "${CYAN}Verificando autenticação no GCP...${NC}"
AUTH_CHECK=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1)
if [ -z "$AUTH_CHECK" ]; then
    echo -e "${YELLOW}⚠️  Não autenticado. Fazendo login...${NC}"
    gcloud auth login
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Falha na autenticação!${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Autenticado como: $AUTH_CHECK${NC}"

# Configurar projeto
echo -e "${CYAN}Configurando projeto...${NC}"
gcloud config set project $PROJECT_ID --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao configurar projeto!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Projeto configurado: $PROJECT_ID${NC}"

# Verificar se service account já existe
echo -e "${CYAN}Verificando se service account já existe...${NC}"
SA_EXISTS=$(gcloud iam service-accounts list --filter="email:$SERVICE_ACCOUNT_EMAIL" --format="value(email)" 2>&1)
if [ "$SA_EXISTS" = "$SERVICE_ACCOUNT_EMAIL" ]; then
    echo -e "${YELLOW}⚠️  Service account já existe: $SERVICE_ACCOUNT_EMAIL${NC}"
    CREATE_SA=false
else
    echo -e "${CYAN}Criando service account...${NC}"
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="GitHub Actions Deploy" \
        --description="Service account para deploy automático via GitHub Actions" \
        --project=$PROJECT_ID \
        --quiet 2>&1
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao criar service account! Pode já existir.${NC}"
        CREATE_SA=false
    else
        echo -e "${GREEN}✅ Service account criada: $SERVICE_ACCOUNT_EMAIL${NC}"
        CREATE_SA=true
    fi
fi

# Atribuir permissões
echo -e "${CYAN}Atribuindo permissões necessárias...${NC}"
ROLES=(
    "roles/run.admin"
    "roles/iam.serviceAccountUser"
    "roles/cloudbuild.builds.editor"
    "roles/storage.admin"
)

for ROLE in "${ROLES[@]}"; do
    echo -e "${CYAN}  Atribuindo: $ROLE${NC}"
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role=$ROLE \
        --condition=None \
        --quiet 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}    ✅ $ROLE atribuída${NC}"
    else
        echo -e "${YELLOW}    ⚠️  $ROLE pode já estar atribuída ou ocorreu erro${NC}"
    fi
done

# Criar chave JSON
echo -e "${CYAN}Criando chave JSON para service account...${NC}"
if [ -f "$KEY_FILE" ]; then
    echo -e "${YELLOW}⚠️  Arquivo $KEY_FILE já existe. Removendo...${NC}"
    rm -f $KEY_FILE
fi

gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL \
    --project=$PROJECT_ID 2>&1

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao criar chave JSON!${NC}"
    exit 1
fi

if [ ! -f "$KEY_FILE" ]; then
    echo -e "${RED}❌ Arquivo de chave não foi criado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Chave JSON criada: $KEY_FILE${NC}"

# Ler conteúdo do arquivo JSON
echo -e "${CYAN}Lendo conteúdo da chave JSON...${NC}"
KEY_CONTENT=$(cat $KEY_FILE)
if [ -z "$KEY_CONTENT" ]; then
    echo -e "${RED}❌ Não foi possível ler o conteúdo da chave JSON!${NC}"
    exit 1
fi

echo ""
echo "========================================"
echo -e "${GREEN}✅ CONFIGURAÇÃO GCP CONCLUÍDA!${NC}"
echo "========================================"
echo ""

echo -e "${YELLOW}📋 PRÓXIMOS PASSOS:${NC}"
echo ""
echo -e "${CYAN}1. Adicione o secret no GitHub:${NC}"
echo "   - Acesse: https://github.com/LMONCAO/monpec/settings/secrets/actions"
echo "   - Clique em 'New repository secret'"
echo "   - Nome: GCP_SA_KEY"
echo "   - Valor: Cole o conteúdo completo do arquivo '$KEY_FILE'"
echo ""
echo -e "${CYAN}2. O conteúdo da chave está salvo em: $KEY_FILE${NC}"
echo ""

# Perguntar se quer exibir o conteúdo
read -p "Deseja exibir o conteúdo da chave JSON agora? (S/N): " SHOW_CONTENT
if [ "$SHOW_CONTENT" = "S" ] || [ "$SHOW_CONTENT" = "s" ]; then
    echo ""
    echo "=== CONTEÚDO DA CHAVE JSON ==="
    echo "$KEY_CONTENT"
    echo "=== FIM DO CONTEÚDO ==="
    echo ""
    echo -e "${CYAN}💡 Copie TODO o conteúdo acima e cole no GitHub como valor do secret 'GCP_SA_KEY'${NC}"
    echo ""
fi

echo -e "${CYAN}3. Após adicionar o secret no GitHub, faça commit e push:${NC}"
echo "   git add .github/"
echo "   git commit -m 'Adicionar GitHub Actions para deploy automático'"
echo "   git push origin main"
echo ""

echo -e "${CYAN}4. O deploy será executado automaticamente no GitHub Actions!${NC}"
echo "   Acompanhe em: https://github.com/LMONCAO/monpec/actions"
echo ""

echo -e "${YELLOW}⚠️  IMPORTANTE: Mantenha o arquivo '$KEY_FILE' seguro e não o commite no Git!${NC}"
echo "   Já adicionado ao .gitignore para evitar commits acidentais."
echo ""

# Adicionar ao .gitignore se não estiver lá
if [ -f ".gitignore" ]; then
    if ! grep -q "github-actions-key\.json" .gitignore; then
        echo "" >> .gitignore
        echo "# GitHub Actions key" >> .gitignore
        echo "github-actions-key.json" >> .gitignore
        echo -e "${GREEN}✅ Arquivo .gitignore atualizado${NC}"
    fi
else
    echo "# GitHub Actions key" > .gitignore
    echo "github-actions-key.json" >> .gitignore
    echo -e "${GREEN}✅ Arquivo .gitignore criado${NC}"
fi

echo -e "${GREEN}✅ Script concluído!${NC}"
echo ""








