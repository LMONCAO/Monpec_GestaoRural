#!/bin/bash
# 🔧 CORREÇÃO DO ERRO 503 - MONPEC.COM.BR NO GOOGLE CLOUD RUN

echo "🔧 CORRIGINDO ERRO 503 - MONPEC.COM.BR (CLOUD RUN)"
echo "=================================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
DOMAIN="monpec.com.br"

# 1. VERIFICAR PROJETO ATIVO
log "1/10 - Verificando projeto ativo..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    warning "Projeto atual: $CURRENT_PROJECT"
    log "Configurando projeto para: $PROJECT_ID"
    gcloud config set project $PROJECT_ID
    if [ $? -eq 0 ]; then
        success "Projeto configurado!"
    else
        error "Falha ao configurar projeto!"
        exit 1
    fi
else
    success "Projeto correto: $PROJECT_ID"
fi
echo ""

# 2. VERIFICAR STATUS DO SERVIÇO CLOUD RUN
log "2/10 - Verificando status do serviço Cloud Run..."
SERVICE_STATUS=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.conditions[0].status)' 2>/dev/null)

if [ -z "$SERVICE_STATUS" ]; then
    error "Serviço '$SERVICE_NAME' não encontrado na região $REGION!"
    warning "Tentando listar serviços disponíveis..."
    gcloud run services list --region $REGION
    echo ""
    warning "Se o serviço não existir, você precisa fazer o deploy primeiro."
    exit 1
fi

if [ "$SERVICE_STATUS" = "True" ]; then
    success "Serviço está ativo!"
else
    error "Serviço não está ativo! Status: $SERVICE_STATUS"
    warning "Verificando detalhes..."
    gcloud run services describe $SERVICE_NAME --region $REGION --format 'yaml(status)' | head -20
fi
echo ""

# 3. VERIFICAR URL DO SERVIÇO
log "3/10 - Verificando URL do serviço..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' 2>/dev/null)

if [ -z "$SERVICE_URL" ]; then
    error "Não foi possível obter URL do serviço!"
else
    success "URL do serviço: $SERVICE_URL"
fi
echo ""

# 4. TESTAR CONECTIVIDADE DO SERVIÇO
log "4/10 - Testando conectividade do serviço..."
if [ -n "$SERVICE_URL" ]; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$SERVICE_URL" 2>/dev/null)
    
    if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
        success "Serviço respondendo! (HTTP $HTTP_STATUS)"
    else
        error "Serviço não está respondendo corretamente! (HTTP $HTTP_STATUS)"
        warning "Isso pode ser a causa do erro 503"
    fi
else
    warning "Não foi possível testar - URL não disponível"
fi
echo ""

# 5. VERIFICAR DOMÍNIO MAPEADO
log "5/10 - Verificando mapeamento do domínio..."
DOMAIN_MAPPING=$(gcloud run domain-mappings describe $DOMAIN --region $REGION --format 'value(status.conditions[0].status)' 2>/dev/null)

if [ -z "$DOMAIN_MAPPING" ]; then
    warning "Domínio '$DOMAIN' não está mapeado!"
    warning "Isso pode ser a causa do erro 503"
    echo ""
    log "Para mapear o domínio, execute:"
    echo "   gcloud run domain-mappings create \\"
    echo "       --service $SERVICE_NAME \\"
    echo "       --domain $DOMAIN \\"
    echo "       --region $REGION"
else
    if [ "$DOMAIN_MAPPING" = "True" ]; then
        success "Domínio está mapeado e ativo!"
    else
        warning "Domínio mapeado mas status: $DOMAIN_MAPPING"
        gcloud run domain-mappings describe $DOMAIN --region $REGION --format 'yaml(status)' | head -10
    fi
fi
echo ""

# 6. VERIFICAR LOGS RECENTES
log "6/10 - Verificando logs recentes do serviço..."
echo "=== ÚLTIMOS 20 LOGS ==="
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit 20 --format "table(timestamp,severity,textPayload)" --project $PROJECT_ID 2>/dev/null | head -25
echo ""

# 7. VERIFICAR REVISÕES ATIVAS
log "7/10 - Verificando revisões ativas..."
REVISIONS=$(gcloud run revisions list --service $SERVICE_NAME --region $REGION --format 'value(metadata.name)' --limit 1 2>/dev/null)

if [ -n "$REVISIONS" ]; then
    success "Revisões encontradas: $(echo $REVISIONS | wc -w)"
    LATEST_REVISION=$(echo $REVISIONS | head -1)
    log "Última revisão: $LATEST_REVISION"
    
    # Verificar status da revisão
    REVISION_STATUS=$(gcloud run revisions describe $LATEST_REVISION --region $REGION --format 'value(status.conditions[0].status)' 2>/dev/null)
    if [ "$REVISION_STATUS" = "True" ]; then
        success "Revisão está ativa!"
    else
        warning "Revisão pode ter problemas. Status: $REVISION_STATUS"
    fi
else
    error "Nenhuma revisão encontrada!"
    warning "O serviço pode não ter sido implantado corretamente"
fi
echo ""

# 8. VERIFICAR CONFIGURAÇÃO DO SERVIÇO
log "8/10 - Verificando configuração do serviço..."
echo "=== CONFIGURAÇÃO ATUAL ==="
gcloud run services describe $SERVICE_NAME --region $REGION --format 'yaml(spec)' | head -30
echo ""

# 9. VERIFICAR PROBLEMAS DE FATURAMENTO
log "9/10 - Verificando status do projeto..."
BILLING_ENABLED=$(gcloud beta billing projects describe $PROJECT_ID --format 'value(billingAccountName)' 2>/dev/null)

if [ -z "$BILLING_ENABLED" ]; then
    error "⚠️  ATENÇÃO: Problema com faturamento detectado!"
    warning "O aviso no console indica que o pagamento não foi processado"
    warning "Isso pode causar suspensão de serviços e erro 503"
    echo ""
    log "Ações necessárias:"
    echo "   1. Acesse: https://console.cloud.google.com/billing"
    echo "   2. Verifique e atualize as informações de pagamento"
    echo "   3. Aguarde alguns minutos após atualizar"
else
    success "Faturamento configurado: $BILLING_ENABLED"
fi
echo ""

# 10. TENTAR REIMPLANTAR (SE NECESSÁRIO)
log "10/10 - Verificando se é necessário reimplantar..."
if [ "$HTTP_STATUS" != "200" ] && [ "$HTTP_STATUS" != "302" ] && [ "$HTTP_STATUS" != "301" ]; then
    warning "Serviço não está respondendo corretamente"
    echo ""
    read -p "Deseja tentar atualizar o serviço? (s/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        log "Atualizando serviço..."
        gcloud run services update $SERVICE_NAME \
            --region $REGION \
            --no-traffic \
            --tag latest
        
        if [ $? -eq 0 ]; then
            success "Serviço atualizado!"
            log "Aguardando 30 segundos para estabilizar..."
            sleep 30
            
            # Testar novamente
            HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "$SERVICE_URL" 2>/dev/null)
            if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
                success "Serviço agora está respondendo! (HTTP $HTTP_STATUS)"
            fi
        else
            error "Falha ao atualizar serviço"
        fi
    fi
else
    success "Serviço está respondendo corretamente"
fi
echo ""

# RESUMO FINAL
echo "=================================================="
echo "🔍 DIAGNÓSTICO CONCLUÍDO!"
echo "=================================================="
echo ""

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ] || [ "$HTTP_STATUS" = "301" ]; then
    success "✅ SERVIÇO ESTÁ FUNCIONANDO!"
    echo ""
    echo "🌐 URLs:"
    echo "   Cloud Run: $SERVICE_URL"
    echo "   Domínio:  https://$DOMAIN"
    echo ""
else
    error "❌ AINDA HÁ PROBLEMAS!"
    echo ""
    echo "📋 Possíveis causas:"
    echo "   1. Problema de faturamento (verifique no console)"
    echo "   2. Serviço não está rodando corretamente"
    echo "   3. Domínio não está mapeado"
    echo "   4. Erros na aplicação (verifique logs)"
    echo ""
    echo "💡 Próximos passos:"
    echo "   1. Verifique faturamento: https://console.cloud.google.com/billing"
    echo "   2. Verifique logs: gcloud logging read \"resource.type=cloud_run_revision\" --limit 50"
    echo "   3. Reimplante se necessário: bash deploy_cloud_shell.sh"
fi

echo ""
echo "💡 Comandos úteis:"
echo "   - Ver status: gcloud run services describe $SERVICE_NAME --region $REGION"
echo "   - Ver logs: gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit 50"
echo "   - Ver domínio: gcloud run domain-mappings describe $DOMAIN --region $REGION"
echo ""


