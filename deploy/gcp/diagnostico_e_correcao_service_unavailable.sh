#!/bin/bash
# 🔍 Script Completo de Diagnóstico e Correção: Service Unavailable no Google Cloud Run
# Este script diagnostica e corrige o erro 503 no Cloud Run

set -e

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
echo "  DIAGNÓSTICO: Service Unavailable (503)"
echo "  Google Cloud Run - Sistema MONPEC"
echo "========================================"
echo ""

# Configurações
PROJECT_ID="${GCP_PROJECT:-monpec-sistema-rural}"
SERVICE_NAME="${CLOUD_RUN_SERVICE:-monpec}"
REGION="${CLOUD_RUN_REGION:-us-central1}"

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

# Configurar projeto
print_step "Configurando projeto: $PROJECT_ID"
gcloud config set project "$PROJECT_ID" --quiet
print_success "Projeto configurado"

# 1. Verificar se o serviço existe
print_step "1️⃣ Verificando se o serviço Cloud Run existe..."
if gcloud run services describe "$SERVICE_NAME" --region="$REGION" &>/dev/null; then
    print_success "Serviço '$SERVICE_NAME' encontrado"
else
    print_error "Serviço '$SERVICE_NAME' NÃO encontrado na região $REGION!"
    echo ""
    echo "Serviços disponíveis:"
    gcloud run services list --region="$REGION" --format="table(metadata.name,status.url,status.conditions[0].status)"
    exit 1
fi

# 2. Verificar status do serviço
print_step "2️⃣ Verificando status do serviço..."
SERVICE_STATUS=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "")

if [ "$SERVICE_STATUS" = "True" ]; then
    print_success "Serviço está ativo"
    [ -n "$SERVICE_URL" ] && print_info "URL: $SERVICE_URL"
else
    print_error "Serviço está com problemas!"
    print_info "Status: $SERVICE_STATUS"
fi

# 3. Verificar logs recentes
print_step "3️⃣ Verificando logs recentes (últimas 50 linhas)..."
echo "----------------------------------------"
gcloud run services logs read "$SERVICE_NAME" --region="$REGION" --limit=50 --format="table(timestamp,severity,textPayload)" 2>/dev/null || \
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=50 --format="table(timestamp,severity,textPayload)" --project="$PROJECT_ID" 2>/dev/null || \
print_warning "Não foi possível ler os logs"
echo ""

# 4. Verificar configuração do serviço
print_step "4️⃣ Verificando configuração do serviço..."
echo "----------------------------------------"
echo "Imagem:"
gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].image)" 2>/dev/null || print_warning "Não foi possível obter a imagem"
echo ""
echo "Variáveis de ambiente:"
gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].env)" 2>/dev/null | head -n 20 || print_warning "Não foi possível obter variáveis de ambiente"
echo ""
echo "Cloud SQL Connections:"
gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || print_warning "Nenhuma conexão Cloud SQL configurada"
echo ""

# 5. Verificar se há instâncias rodando
print_step "5️⃣ Verificando instâncias ativas..."
REVISIONS=$(gcloud run revisions list --service="$SERVICE_NAME" --region="$REGION" --format="value(metadata.name)" --limit=1 2>/dev/null || echo "")
if [ -n "$REVISIONS" ]; then
    print_success "Revisões encontradas"
    echo "Última revisão: $REVISIONS"
else
    print_error "Nenhuma revisão encontrada!"
fi
echo ""

# 6. Testar conexão HTTP
print_step "6️⃣ Testando conexão HTTP..."
if [ -n "$SERVICE_URL" ]; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" 2>/dev/null || echo "000")
    if [ "$HTTP_STATUS" = "200" ]; then
        print_success "Serviço responde com HTTP 200"
    elif [ "$HTTP_STATUS" = "503" ]; then
        print_error "Serviço retorna HTTP 503 (Service Unavailable)"
    elif [ "$HTTP_STATUS" = "000" ]; then
        print_warning "Não foi possível conectar ao serviço"
    else
        print_warning "Serviço retorna HTTP $HTTP_STATUS"
    fi
else
    print_warning "URL do serviço não disponível para teste"
fi
echo ""

# 7. Verificar Cloud SQL
print_step "7️⃣ Verificando Cloud SQL..."
DB_INSTANCE="monpec-db"
if gcloud sql instances describe "$DB_INSTANCE" &>/dev/null; then
    print_success "Instância Cloud SQL '$DB_INSTANCE' existe"
    DB_STATUS=$(gcloud sql instances describe "$DB_INSTANCE" --format="value(state)" 2>/dev/null || echo "Unknown")
    print_info "Status: $DB_STATUS"
    
    if [ "$DB_STATUS" != "RUNNABLE" ]; then
        print_warning "Cloud SQL não está em estado RUNNABLE!"
    fi
else
    print_warning "Instância Cloud SQL '$DB_INSTANCE' não encontrada"
fi
echo ""

# 8. Tentar correção automática
echo "========================================"
echo "🔧 TENTANDO CORREÇÃO AUTOMÁTICA"
echo "========================================"
echo ""

# 8.1 Verificar e atualizar variáveis de ambiente críticas
print_step "8.1 Verificando variáveis de ambiente críticas..."
CURRENT_ENV=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")

# Verificar se DJANGO_SETTINGS_MODULE está configurado
if echo "$CURRENT_ENV" | grep -q "DJANGO_SETTINGS_MODULE"; then
    print_success "DJANGO_SETTINGS_MODULE está configurado"
else
    print_warning "DJANGO_SETTINGS_MODULE não encontrado. Adicionando..."
    gcloud run services update "$SERVICE_NAME" \
        --region="$REGION" \
        --update-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
        --quiet
    print_success "Variável adicionada"
fi

# 8.2 Verificar Cloud SQL connection
print_step "8.2 Verificando conexão Cloud SQL..."
CLOUD_SQL_CONN=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_CONN" ] && gcloud sql instances describe "$DB_INSTANCE" &>/dev/null; then
    print_warning "Cloud SQL connection não configurada. Configurando..."
    CONNECTION_NAME=$(gcloud sql instances describe "$DB_INSTANCE" --format="value(connectionName)" 2>/dev/null || echo "")
    if [ -n "$CONNECTION_NAME" ]; then
        gcloud run services update "$SERVICE_NAME" \
            --region="$REGION" \
            --add-cloudsql-instances="$CONNECTION_NAME" \
            --quiet
        print_success "Cloud SQL connection configurada: $CONNECTION_NAME"
    fi
else
    print_success "Cloud SQL connection já está configurada"
fi

# 8.3 Verificar recursos (CPU/Memória)
print_step "8.3 Verificando recursos do serviço..."
CURRENT_MEMORY=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].resources.limits.memory)" 2>/dev/null || echo "")
CURRENT_CPU=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.containers[0].resources.limits.cpu)" 2>/dev/null || echo "")

print_info "Memória atual: ${CURRENT_MEMORY:-Não definida}"
print_info "CPU atual: ${CURRENT_CPU:-Não definida}"

# Se memória for muito baixa, aumentar
if [ -z "$CURRENT_MEMORY" ] || [ "$CURRENT_MEMORY" = "256Mi" ] || [ "$CURRENT_MEMORY" = "512Mi" ]; then
    print_warning "Memória pode estar muito baixa. Aumentando para 2Gi..."
    gcloud run services update "$SERVICE_NAME" \
        --region="$REGION" \
        --memory=2Gi \
        --cpu=2 \
        --quiet
    print_success "Recursos atualizados: 2Gi RAM, 2 CPU"
fi

# 8.4 Verificar min-instances (evitar cold start)
print_step "8.4 Verificando min-instances..."
CURRENT_MIN_INSTANCES=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.metadata.annotations.'autoscaling.knative.dev/minScale')" 2>/dev/null || echo "0")

if [ "$CURRENT_MIN_INSTANCES" = "0" ]; then
    print_warning "min-instances está em 0 (pode causar cold start). Aumentando para 1..."
    gcloud run services update "$SERVICE_NAME" \
        --region="$REGION" \
        --min-instances=1 \
        --quiet
    print_success "min-instances atualizado para 1"
else
    print_success "min-instances: $CURRENT_MIN_INSTANCES"
fi

# 8.5 Verificar timeout
print_step "8.5 Verificando timeout..."
CURRENT_TIMEOUT=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(spec.template.spec.timeoutSeconds)" 2>/dev/null || echo "300")

if [ "$CURRENT_TIMEOUT" -lt 300 ]; then
    print_warning "Timeout pode estar muito baixo. Aumentando para 300s..."
    gcloud run services update "$SERVICE_NAME" \
        --region="$REGION" \
        --timeout=300 \
        --quiet
    print_success "Timeout atualizado para 300s"
else
    print_success "Timeout: ${CURRENT_TIMEOUT}s"
fi

# 9. Aguardar e verificar novamente
print_step "9️⃣ Aguardando estabilização (10 segundos)..."
sleep 10

# 10. Verificar status final
echo ""
echo "========================================"
echo "📊 STATUS FINAL"
echo "========================================"
echo ""

SERVICE_STATUS_FINAL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.conditions[0].status)" 2>/dev/null || echo "Unknown")
SERVICE_URL_FINAL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null || echo "")

if [ "$SERVICE_STATUS_FINAL" = "True" ]; then
    print_success "✅ Serviço está ATIVO"
else
    print_error "❌ Serviço ainda está com problemas"
fi

if [ -n "$SERVICE_URL_FINAL" ]; then
    print_info "URL: $SERVICE_URL_FINAL"
    
    # Testar novamente
    HTTP_STATUS_FINAL=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL_FINAL" 2>/dev/null || echo "000")
    if [ "$HTTP_STATUS_FINAL" = "200" ]; then
        print_success "✅ Serviço responde com HTTP 200"
    elif [ "$HTTP_STATUS_FINAL" = "503" ]; then
        print_error "❌ Serviço ainda retorna HTTP 503"
        echo ""
        echo "Possíveis causas restantes:"
        echo "  1. Erro na aplicação Django (verifique logs)"
        echo "  2. Problema de conexão com Cloud SQL"
        echo "  3. Variáveis de ambiente faltando ou incorretas"
        echo "  4. Erro no código da aplicação"
    else
        print_warning "⚠️ Serviço retorna HTTP $HTTP_STATUS_FINAL"
    fi
fi

echo ""
echo "========================================"
echo "📋 PRÓXIMOS PASSOS"
echo "========================================"
echo ""
echo "Se o problema persistir:"
echo ""
echo "1. Ver logs detalhados:"
echo "   gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=100"
echo ""
echo "2. Ver logs em tempo real:"
echo "   gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo ""
echo "3. Verificar variáveis de ambiente:"
echo "   gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(spec.template.spec.containers[0].env)'"
echo ""
echo "4. Verificar Cloud SQL:"
echo "   gcloud sql instances describe monpec-db"
echo ""
echo "5. Fazer novo deploy se necessário:"
echo "   bash scripts/deploy/deploy-gcp.sh"
echo ""
echo "6. Verificar se o domínio está configurado corretamente:"
echo "   gcloud run domain-mappings list --region=$REGION"
echo ""
