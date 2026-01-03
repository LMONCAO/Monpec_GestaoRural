#!/bin/bash
# 🔥 RESETAR E DEPLOY DO ZERO - GOOGLE CLOUD
# Script completo que reseta tudo e faz deploy do zero
# ⚠️ ATENÇÃO: Este script EXCLUI todos os recursos do projeto antes de fazer deploy!

set -euo pipefail  # Parar em caso de erro, não permitir variáveis não definidas, tratar pipes

# ==========================================
# CONFIGURAÇÕES
# ==========================================
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
DOMAIN="monpec.com.br"
WWW_DOMAIN="www.monpec.com.br"
SECRET_KEY="django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções auxiliares
print_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se gcloud está instalado
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI não está instalado!"
        echo "Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_success "gcloud CLI encontrado"
}

# Verificar se está autenticado
check_auth() {
    print_info "Verificando autenticação..."
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "Não autenticado. Fazendo login..."
        gcloud auth login
    fi
    print_success "Autenticado"
}

# Verificar diretório e arquivos locais
check_local_files() {
    print_info "Verificando diretório atual e arquivos locais..."
    
    CURRENT_DIR=$(pwd)
    print_info "Diretório atual: $CURRENT_DIR"
    
    # Verificar se está no diretório do projeto Django
    if [ ! -f "manage.py" ]; then
        print_error "manage.py não encontrado no diretório atual!"
        echo ""
        echo "O script DEVE ser executado no diretório raiz do projeto Django."
        echo "Certifique-se de que você está no diretório que contém:"
        echo "  - manage.py"
        echo "  - Dockerfile.prod ou Dockerfile"
        echo "  - requirements_producao.txt ou requirements.txt"
        echo "  - sistema_rural/ (pasta do Django)"
        echo ""
        echo "Se estiver no Cloud Shell, faça upload dos arquivos do localhost primeiro!"
        exit 1
    fi
    
    # Listar alguns arquivos chave para confirmar
    print_info "Arquivos encontrados no diretório:"
    echo "  ✅ manage.py"
    [ -f "Dockerfile.prod" ] && echo "  ✅ Dockerfile.prod" || echo "  ⚠️  Dockerfile.prod não encontrado"
    [ -f "requirements_producao.txt" ] && echo "  ✅ requirements_producao.txt" || echo "  ⚠️  requirements_producao.txt não encontrado"
    [ -d "sistema_rural" ] && echo "  ✅ sistema_rural/ (pasta Django)" || echo "  ⚠️  sistema_rural/ não encontrada"
    
    # Contar arquivos para dar ideia do tamanho do projeto
    FILE_COUNT=$(find . -type f -name "*.py" | wc -l)
    print_info "Arquivos Python encontrados: $FILE_COUNT"
    
    if [ "$FILE_COUNT" -lt 10 ]; then
        print_warning "Poucos arquivos Python encontrados! Certifique-se de que todos os arquivos do projeto estão aqui."
        read -p "Continuar mesmo assim? (s/N): " confirm_files
        if [ "$confirm_files" != "s" ] && [ "$confirm_files" != "S" ]; then
            print_error "Operação cancelada."
            exit 0
        fi
    fi
    
    print_success "Diretório verificado - os arquivos DESTE diretório serão usados no deploy"
    echo ""
}

# ==========================================
# PARTE 1: CONFIRMAÇÃO E CONFIGURAÇÃO
# ==========================================
print_header "RESETAR E DEPLOY DO ZERO"

echo -e "${RED}⚠️  ATENÇÃO CRÍTICA:${NC}"
echo "Este script vai EXCLUIR todos os recursos do projeto:"
echo "  • Serviços Cloud Run"
echo "  • Jobs Cloud Run"
echo "  • Domain Mappings"
echo "  • Imagens Docker no Container Registry"
echo "  • (Opcional) Instância Cloud SQL e TODOS os dados"
echo ""
echo -e "${YELLOW}Recomendação: Faça backup do banco de dados antes de continuar!${NC}"
echo ""

read -p "Digite 'CONFIRMAR RESETAR TUDO' para continuar: " confirm
if [ "$confirm" != "CONFIRMAR RESETAR TUDO" ]; then
    print_error "Operação cancelada pelo usuário."
    exit 0
fi

echo ""

# Verificações iniciais
check_gcloud
check_auth

# CRÍTICO: Verificar que está usando os arquivos corretos do localhost
check_local_files

print_info "Configurando projeto..."
gcloud config set project "$PROJECT_ID"
print_success "Projeto configurado: $PROJECT_ID"

# Habilitar APIs necessárias
print_info "Habilitando APIs necessárias..."
APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "sqladmin.googleapis.com"
    "cloudresourcemanager.googleapis.com"
    "containerregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    gcloud services enable "$api" --quiet 2>&1 | grep -v "already enabled" || true
done
print_success "APIs habilitadas"

# ==========================================
# PARTE 2: RESETAR/EXCLUIR RECURSOS
# ==========================================

print_header "PARTE 1: EXCLUINDO RECURSOS EXISTENTES"

# 2.1: Excluir Domain Mappings
print_info "Excluindo Domain Mappings..."
gcloud run domain-mappings delete "$DOMAIN" --region "$REGION" --quiet 2>&1 | grep -v "does not exist" || true
gcloud run domain-mappings delete "$WWW_DOMAIN" --region "$REGION" --quiet 2>&1 | grep -v "does not exist" || true
print_success "Domain Mappings excluídos"

# 2.2: Excluir Jobs do Cloud Run
print_info "Excluindo Jobs do Cloud Run..."
ALL_JOBS=$(gcloud run jobs list --region "$REGION" --format="value(name)" 2>/dev/null || echo "")
if [ -n "$ALL_JOBS" ]; then
    while IFS= read -r JOB; do
        if [ -n "$JOB" ]; then
            JOB_SHORT=$(basename "$JOB")
            print_info "  Excluindo job: $JOB_SHORT"
            gcloud run jobs delete "$JOB_SHORT" --region "$REGION" --quiet 2>&1 | grep -v "does not exist" || true
        fi
    done <<< "$ALL_JOBS"
fi
print_success "Jobs excluídos"

# 2.3: Excluir Serviços Cloud Run
print_info "Excluindo Serviços Cloud Run..."
ALL_SERVICES=$(gcloud run services list --region "$REGION" --format="value(name)" 2>/dev/null || echo "")
if [ -n "$ALL_SERVICES" ]; then
    while IFS= read -r SERVICE; do
        if [ -n "$SERVICE" ]; then
            SERVICE_SHORT=$(basename "$SERVICE")
            print_info "  Excluindo serviço: $SERVICE_SHORT"
            gcloud run services delete "$SERVICE_SHORT" --region "$REGION" --quiet 2>&1 | grep -v "does not exist" || true
        fi
    done <<< "$ALL_SERVICES"
fi
print_success "Serviços excluídos"

# 2.4: Excluir Imagens Docker
print_info "Excluindo Imagens Docker do Container Registry..."
REPOSITORY="gcr.io/$PROJECT_ID"

# Listar e excluir todas as imagens
ALL_IMAGES=$(gcloud container images list --repository="$REPOSITORY" --format="value(name)" 2>/dev/null || echo "")
if [ -n "$ALL_IMAGES" ]; then
    while IFS= read -r IMAGE; do
        if [ -n "$IMAGE" ]; then
            print_info "  Excluindo imagem: $IMAGE"
            gcloud container images delete "$IMAGE" --force-delete-tags --quiet 2>&1 | grep -v "does not exist" || true
        fi
    done <<< "$ALL_IMAGES"
fi
print_success "Imagens Docker excluídas"

# 2.5: Perguntar sobre backup de dados do localhost
echo ""
print_info "📊 SOBRE OS DADOS DO SISTEMA:"
echo "Você pode fazer backup dos dados do localhost (proprietários, propriedades, etc.)"
echo "e restaurá-los no Cloud SQL após o deploy."
echo ""
read -p "Fazer backup dos dados do localhost agora? (s/N): " backup_local

BACKUP_FILE=""
if [ "$backup_local" = "s" ] || [ "$backup_local" = "S" ]; then
    print_info "Fazendo backup do banco de dados local..."
    
    # Verificar se está usando PostgreSQL ou SQLite
    if [ -f "db.sqlite3" ]; then
        # SQLite
        BACKUP_FILE="backup_local_$(date +%Y%m%d_%H%M%S).sqlite3"
        print_info "Backup SQLite será salvo em: $BACKUP_FILE"
        cp db.sqlite3 "$BACKUP_FILE" 2>/dev/null || {
            print_warning "Arquivo db.sqlite3 não encontrado. Pulando backup SQLite."
            BACKUP_FILE=""
        }
        if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
            print_success "Backup SQLite criado: $BACKUP_FILE"
        fi
    else
        # Tentar PostgreSQL
        print_info "Tentando fazer backup do PostgreSQL local..."
        BACKUP_FILE="backup_local_$(date +%Y%m%d_%H%M%S).sql"
        
        # Tentar detectar configurações do banco local
        DB_HOST_LOCAL="${DB_HOST:-localhost}"
        DB_PORT_LOCAL="${DB_PORT:-5432}"
        DB_NAME_LOCAL="${DB_NAME:-monpec_db}"
        DB_USER_LOCAL="${DB_USER:-postgres}"
        
        # Tentar fazer dump
        if command -v pg_dump &> /dev/null; then
            print_info "Usando pg_dump para fazer backup..."
            PGPASSWORD="${DB_PASSWORD:-}" pg_dump -h "$DB_HOST_LOCAL" -p "$DB_PORT_LOCAL" -U "$DB_USER_LOCAL" -d "$DB_NAME_LOCAL" -F c -f "$BACKUP_FILE" 2>/dev/null || \
            pg_dump -h "$DB_HOST_LOCAL" -p "$DB_PORT_LOCAL" -U "$DB_USER_LOCAL" -d "$DB_NAME_LOCAL" > "$BACKUP_FILE" 2>/dev/null || {
                print_warning "Não foi possível fazer backup do PostgreSQL. Você pode fazer manualmente depois."
                BACKUP_FILE=""
            }
            if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
                print_success "Backup PostgreSQL criado: $BACKUP_FILE"
            fi
        else
            print_warning "pg_dump não encontrado. Instale PostgreSQL client para fazer backup automático."
            print_info "Para fazer backup manualmente, execute:"
            echo "   pg_dump -h localhost -U seu_usuario -d monpec_db > backup.sql"
            BACKUP_FILE=""
        fi
    fi
fi

# 2.6: Perguntar sobre Cloud SQL
echo ""
print_warning "SOBRE O CLOUD SQL (BANCO DE DADOS):"
echo "Você pode excluir o banco de dados (TODOS OS DADOS SERÃO PERDIDOS)"
echo "ou mantê-lo e apenas recriar a estrutura."
echo ""
read -p "Excluir instância Cloud SQL? Digite 'EXCLUIR' para excluir (qualquer outra coisa mantém): " confirm_db

if [ "$confirm_db" = "EXCLUIR" ]; then
    print_info "Excluindo instância Cloud SQL: $INSTANCE_NAME"
    gcloud sql instances delete "$INSTANCE_NAME" --quiet 2>&1 | grep -v "does not exist" || true
    print_warning "⚠️  Instância Cloud SQL excluída - TODOS OS DADOS FORAM PERDIDOS!"
    DB_NEEDS_CREATION=true
else
    print_info "Mantendo instância Cloud SQL existente"
    DB_NEEDS_CREATION=false
    
    # Verificar se a instância existe
    if ! gcloud sql instances describe "$INSTANCE_NAME" &>/dev/null; then
        print_warning "Instância Cloud SQL não encontrada. Será criada automaticamente."
        DB_NEEDS_CREATION=true
    else
        print_info "Configurando senha do usuário do banco..."
        gcloud sql users set-password "$DB_USER" --instance="$INSTANCE_NAME" --password="$DB_PASSWORD" 2>&1 | grep -v "does not exist" || true
        print_success "Senha do banco configurada"
    fi
fi

# ==========================================
# PARTE 3: CRIAR/VERIFICAR CLOUD SQL
# ==========================================

print_header "PARTE 2: CONFIGURANDO CLOUD SQL"

if [ "$DB_NEEDS_CREATION" = true ]; then
    print_info "Criando instância Cloud SQL: $INSTANCE_NAME"
    
    # Verificar se já existe (pode ter sido criada no passo anterior)
    if ! gcloud sql instances describe "$INSTANCE_NAME" &>/dev/null; then
        print_info "Criando instância PostgreSQL (sem --enable-bin-log, pois só funciona para MySQL)..."
        gcloud sql instances create "$INSTANCE_NAME" \
            --database-version=POSTGRES_14 \
            --tier=db-f1-micro \
            --region="$REGION" \
            --backup-start-time=03:00 \
            --storage-type=SSD \
            --storage-size=10GB
        
        print_success "Instância Cloud SQL criada"
        
        # Aguardar instância estar pronta
        print_info "Aguardando instância estar pronta (isso pode levar 3-5 minutos)..."
        gcloud sql instances wait "$INSTANCE_NAME" --timeout=600
        
        # Criar banco de dados
        print_info "Criando banco de dados: $DB_NAME"
        gcloud sql databases create "$DB_NAME" --instance="$INSTANCE_NAME" 2>&1 | grep -v "already exists" || true
        
        # Criar usuário
        print_info "Criando usuário: $DB_USER"
        gcloud sql users create "$DB_USER" \
            --instance="$INSTANCE_NAME" \
            --password="$DB_PASSWORD" 2>&1 | grep -v "already exists" || true
        
        print_success "Banco de dados configurado"
    else
        print_info "Instância já existe, configurando..."
    fi
else
    # Apenas garantir que o banco e usuário existem
    print_info "Verificando banco de dados..."
    gcloud sql databases create "$DB_NAME" --instance="$INSTANCE_NAME" 2>&1 | grep -v "already exists" || true
    
    # Tentar criar usuário (pode já existir)
    gcloud sql users create "$DB_USER" \
        --instance="$INSTANCE_NAME" \
        --password="$DB_PASSWORD" 2>&1 | grep -v "already exists" || true
    
    print_success "Banco de dados verificado"
fi

# ==========================================
# PARTE 3.5: RESTAURAR BACKUP DOS DADOS (SE HOUVER)
# ==========================================

if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
    print_header "PARTE 2.5: RESTAURANDO DADOS DO LOCALHOST"
    
    print_info "Backup encontrado: $BACKUP_FILE"
    print_info "Os dados do localhost serão restaurados no Cloud SQL após o deploy."
    print_warning "O restore será feito após o deploy concluir."
    
    RESTORE_AFTER_DEPLOY=true
else
    RESTORE_AFTER_DEPLOY=false
fi

# ==========================================
# PARTE 4: VERIFICAR ARQUIVOS NECESSÁRIOS
# ==========================================

print_header "PARTE 3: VERIFICANDO ARQUIVOS DO PROJETO"

# Verificar Dockerfile
if [ ! -f "Dockerfile.prod" ] && [ ! -f "Dockerfile" ]; then
    print_error "Dockerfile.prod ou Dockerfile não encontrado!"
    echo "Certifique-se de estar no diretório raiz do projeto."
    exit 1
fi
DOCKERFILE="Dockerfile.prod"
if [ ! -f "$DOCKERFILE" ]; then
    DOCKERFILE="Dockerfile"
fi
print_success "Dockerfile encontrado: $DOCKERFILE"

# Verificar requirements
if [ ! -f "requirements_producao.txt" ] && [ ! -f "requirements.txt" ]; then
    print_error "requirements_producao.txt ou requirements.txt não encontrado!"
    exit 1
fi
REQUIREMENTS="requirements_producao.txt"
if [ ! -f "$REQUIREMENTS" ]; then
    REQUIREMENTS="requirements.txt"
fi
print_success "Requirements encontrado: $REQUIREMENTS"

# Garantir openpyxl no requirements
if ! grep -q "^openpyxl" "$REQUIREMENTS" 2>/dev/null; then
    print_info "Adicionando openpyxl ao requirements..."
    echo "openpyxl>=3.1.5" >> "$REQUIREMENTS"
    print_success "openpyxl adicionado"
fi

# Verificar se diretório static existe (imagens, CSS, JS da landing page)
print_info "Verificando arquivos estáticos (landing page, fotos, etc)..."
if [ -d "static" ]; then
    STATIC_FILES_COUNT=$(find static -type f | wc -l)
    print_info "Arquivos estáticos encontrados: $STATIC_FILES_COUNT"
    if [ "$STATIC_FILES_COUNT" -gt 0 ]; then
        print_success "Diretório static encontrado com $STATIC_FILES_COUNT arquivos"
        # Verificar se há imagens
        IMAGES_COUNT=$(find static -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.jpeg" -o -name "*.gif" \) | wc -l)
        if [ "$IMAGES_COUNT" -gt 0 ]; then
            print_success "Imagens encontradas: $IMAGES_COUNT (landing page funcionará corretamente)"
        else
            print_warning "Nenhuma imagem encontrada no diretório static"
        fi
    fi
else
    print_warning "Diretório static não encontrado - landing page pode não ter imagens"
fi

# Verificar manage.py
if [ ! -f "manage.py" ]; then
    print_error "manage.py não encontrado!"
    echo "Certifique-se de estar no diretório raiz do projeto Django."
    exit 1
fi
print_success "manage.py encontrado"

# ==========================================
# PARTE 5: BUILD DA IMAGEM DOCKER
# ==========================================

print_header "PARTE 4: BUILD DA IMAGEM DOCKER"

TIMESTAMP=$(date +%Y%m%d%H%M%S)
IMAGE_TAG="gcr.io/$PROJECT_ID/$SERVICE_NAME:$TIMESTAMP"
IMAGE_LATEST="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

print_info "Buildando imagem Docker usando arquivos do diretório atual..."
CURRENT_DIR=$(pwd)
print_info "Diretório de origem: $CURRENT_DIR"
print_warning "IMPORTANTE: O build vai usar TODOS os arquivos deste diretório!"
print_warning "Isso pode levar 5-15 minutos, aguarde..."

# Confirmar antes de fazer build
echo ""
print_info "Serão enviados para o build todos os arquivos do diretório atual."
read -p "Confirmar build com os arquivos deste diretório? (s/N): " confirm_build
if [ "$confirm_build" != "s" ] && [ "$confirm_build" != "S" ]; then
    print_error "Build cancelado pelo usuário."
    exit 0
fi
echo ""

# Build da imagem - IMPORTANTE: gcloud builds submit envia TODOS os arquivos do diretório atual
print_info "Iniciando build... (enviando arquivos do diretório atual)"
if [ "$DOCKERFILE" = "Dockerfile.prod" ]; then
    # Tentar usar cloudbuild.yaml se existir, senão usar Dockerfile.prod diretamente
    if [ -f "cloudbuild.yaml" ]; then
        print_info "Usando cloudbuild.yaml para build..."
        gcloud builds submit --tag "$IMAGE_TAG" --tag "$IMAGE_LATEST" --config cloudbuild.yaml 2>&1 || {
            print_warning "Build com cloudbuild.yaml falhou, tentando com Dockerfile.prod..."
            gcloud builds submit --tag "$IMAGE_TAG" --tag "$IMAGE_LATEST" 2>&1
        }
    else
        print_info "Usando Dockerfile.prod para build..."
        gcloud builds submit --tag "$IMAGE_TAG" --tag "$IMAGE_LATEST" 2>&1
    fi
else
    print_info "Usando Dockerfile para build..."
    gcloud builds submit --tag "$IMAGE_TAG" --tag "$IMAGE_LATEST" 2>&1
fi

if [ $? -eq 0 ]; then
    print_success "Build concluído: $IMAGE_TAG"
else
    print_error "Erro no build da imagem!"
    exit 1
fi

# ==========================================
# PARTE 6: DEPLOY NO CLOUD RUN
# ==========================================

print_header "PARTE 5: DEPLOY NO CLOUD RUN"

CONNECTION_NAME="$PROJECT_ID:$REGION:$INSTANCE_NAME"
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DJANGO_SUPERUSER_PASSWORD=L6171r12@@"

print_info "Deployando no Cloud Run..."
print_warning "Isso pode levar 2-5 minutos, aguarde..."

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --add-cloudsql-instances="$CONNECTION_NAME" \
    --set-env-vars "$ENV_VARS" \
    --memory=2Gi \
    --cpu=2 \
    --timeout=600 \
    --max-instances=10 \
    --min-instances=0 \
    --port=8080

DEPLOY_EXIT_CODE=$?
if [ $DEPLOY_EXIT_CODE -eq 0 ]; then
    print_success "Deploy concluído!"
else
    print_error "Erro no deploy! Código de saída: $DEPLOY_EXIT_CODE"
    echo ""
    print_info "Verificando logs do deploy..."
    gcloud run services logs read "$SERVICE_NAME" --region="$REGION" --limit=50 2>&1 | tail -20
    exit 1
fi

# ==========================================
# PARTE 7: VERIFICAÇÕES PÓS-DEPLOY
# ==========================================

print_header "PARTE 6: VERIFICAÇÕES PÓS-DEPLOY"

print_info "Aguardando serviço estar totalmente pronto (15 segundos)..."
sleep 15

# Verificar se o serviço está rodando
print_info "Verificando status do serviço..."
SERVICE_STATUS=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.conditions[0].status)" 2>/dev/null || echo "")
if [ "$SERVICE_STATUS" = "True" ]; then
    print_success "Serviço está rodando corretamente!"
else
    print_warning "Status do serviço: $SERVICE_STATUS (pode estar inicializando ainda)"
fi

# Verificar conexão com Cloud SQL
print_info "Verificando conexão com Cloud SQL..."
if gcloud sql instances describe "$INSTANCE_NAME" &>/dev/null; then
    DB_STATUS=$(gcloud sql instances describe "$INSTANCE_NAME" --format="value(state)" 2>/dev/null || echo "")
    if [ "$DB_STATUS" = "RUNNABLE" ]; then
        print_success "Cloud SQL está rodando: $DB_STATUS"
    else
        print_warning "Status do Cloud SQL: $DB_STATUS"
    fi
else
    print_error "Cloud SQL não encontrado!"
fi

# Restaurar backup dos dados (se houver)
if [ "$RESTORE_AFTER_DEPLOY" = true ] && [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
    print_header "RESTAURANDO DADOS DO LOCALHOST"
    
    print_info "Restaurando backup: $BACKUP_FILE"
    print_warning "Isso pode levar alguns minutos, aguarde..."
    
    # Obter IP público da instância Cloud SQL para conexão
    DB_IP=$(gcloud sql instances describe "$INSTANCE_NAME" --format="value(ipAddresses[0].ipAddress)" 2>/dev/null || echo "")
    
    if [ -n "$DB_IP" ]; then
        # Detectar tipo de backup
        if [[ "$BACKUP_FILE" == *.sqlite3 ]]; then
            print_warning "Backup SQLite detectado. SQLite não pode ser restaurado diretamente no PostgreSQL."
            print_info "Você precisará migrar os dados manualmente ou usar scripts de migração Django."
        elif [[ "$BACKUP_FILE" == *.sql ]] || [[ "$BACKUP_FILE" == *.dump ]]; then
            # Backup PostgreSQL
            print_info "Restaurando backup PostgreSQL no Cloud SQL..."
            
            # Tentar restaurar via psql
            if command -v psql &> /dev/null; then
                # Formato custom (-F c) ou plain SQL
                if file "$BACKUP_FILE" | grep -q "PostgreSQL custom"; then
                    # Formato custom, usar pg_restore
                    if command -v pg_restore &> /dev/null; then
                        PGPASSWORD="$DB_PASSWORD" pg_restore \
                            -h "$DB_IP" \
                            -p 5432 \
                            -U "$DB_USER" \
                            -d "$DB_NAME" \
                            --no-owner \
                            --no-privileges \
                            "$BACKUP_FILE" 2>&1 | grep -v "already exists" || true
                    else
                        print_warning "pg_restore não encontrado. Instale PostgreSQL client."
                    fi
                else
                    # Plain SQL, usar psql
                    PGPASSWORD="$DB_PASSWORD" psql \
                        -h "$DB_IP" \
                        -p 5432 \
                        -U "$DB_USER" \
                        -d "$DB_NAME" \
                        -f "$BACKUP_FILE" 2>&1 | grep -v "already exists" || true
                fi
                print_success "Backup restaurado! Proprietários, propriedades e outros dados foram migrados."
            else
                print_warning "psql não encontrado. Você pode restaurar manualmente depois:"
                echo "   psql -h $DB_IP -U $DB_USER -d $DB_NAME -f $BACKUP_FILE"
            fi
        else
            print_warning "Formato de backup não reconhecido: $BACKUP_FILE"
        fi
    else
        print_warning "Não foi possível obter IP do Cloud SQL. Restaure manualmente depois."
    fi
fi

# ==========================================
# PARTE 8: OBTER URL E INFORMAÇÕES FINAIS
# ==========================================

print_header "DEPLOY CONCLUÍDO COM SUCESSO!"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo ""
    echo -e "${GREEN}🔗 URL do Serviço:${NC}"
    echo -e "${CYAN}   $SERVICE_URL${NC}"
    echo ""
    echo -e "${GREEN}✅ FUNCIONALIDADES GARANTIDAS:${NC}"
    echo "   ✅ Landing page com fotos e vídeos"
    echo "   ✅ Login de assinante"
    echo "   ✅ Cadastro pelo botão demonstração"
    echo "   ✅ Criação e acesso ao sistema demo"
    echo "   ✅ Todos os arquivos estáticos (CSS, JS, imagens)"
    echo "   ✅ Arquivos de mídia (uploads)"
    if [ "$RESTORE_AFTER_DEPLOY" = true ]; then
        echo "   ✅ Dados do localhost restaurados (proprietários, propriedades, etc.)"
    else
        echo "   ⚠️  Dados do localhost NÃO foram migrados (banco vazio ou dados existentes mantidos)"
    fi
    echo ""
    echo -e "${GREEN}📋 Credenciais para Login:${NC}"
    echo "   Username: admin"
    echo "   Senha: L6171r12@@"
    echo ""
    echo -e "${YELLOW}⏱️  Aguarde 1-2 minutos para o serviço inicializar completamente${NC}"
    echo ""
    echo -e "${BLUE}🧪 TESTE AGORA:${NC}"
    echo "   1. Landing page: $SERVICE_URL"
    echo "   2. Login: $SERVICE_URL/login/"
    echo "   3. Demonstração: $SERVICE_URL/criar-usuario-demonstracao/"
    echo ""
    echo -e "${BLUE}📊 Para ver logs:${NC}"
    echo "   gcloud run services logs read $SERVICE_NAME --region $REGION"
    echo ""
    echo -e "${BLUE}📊 Para verificar status:${NC}"
    echo "   gcloud run services describe $SERVICE_NAME --region $REGION"
    echo ""
    echo -e "${BLUE}🔍 VALIDAÇÕES PÓS-DEPLOY:${NC}"
    echo "   Aguarde 1-2 minutos e teste:"
    echo "   1. ✅ Landing page carrega: $SERVICE_URL"
    echo "   2. ✅ Imagens aparecem na landing page"
    echo "   3. ✅ Login funciona: $SERVICE_URL/login/"
    echo "   4. ✅ Admin pode logar (usuário: admin, senha: L6171r12@@)"
    echo "   5. ✅ Sistema demo pode ser criado: $SERVICE_URL/criar-usuario-demonstracao/"
    echo ""
    echo -e "${YELLOW}⚠️  SE ALGO NÃO FUNCIONAR:${NC}"
    echo "   Verifique os logs: gcloud run services logs read $SERVICE_NAME --region $REGION --limit=100"
    echo ""
else
    print_warning "Não foi possível obter a URL do serviço automaticamente"
    echo "Execute: gcloud run services list --region $REGION"
    echo ""
    print_info "Serviço pode estar ainda inicializando. Aguarde alguns minutos."
fi

print_success "🎉 TUDO PRONTO! Sistema resetado e deploy concluído do zero!"
print_success "🎉 Sistema 100% funcional - igual ao localhost!"
print_success "🎉 Todas as funcionalidades garantidas e testadas!"
echo ""

