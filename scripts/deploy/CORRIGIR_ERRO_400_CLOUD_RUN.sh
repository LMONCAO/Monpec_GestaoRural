#!/bin/bash
# Script para diagnosticar e corrigir erro 400 no Cloud Run
# Execute este script no Cloud Shell do Google Cloud

set -e

echo "=========================================="
echo "🔍 DIAGNÓSTICO E CORREÇÃO - ERRO 400"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"

echo "📋 Verificando configurações do projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando variáveis de ambiente do serviço..."
echo "----------------------------------------"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env)" || echo "⚠️ Erro ao obter variáveis de ambiente"

echo ""
echo "2️⃣ Verificando logs recentes do serviço..."
echo "----------------------------------------"
echo "Últimas 50 linhas de log:"
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
    --limit=50 \
    --format="table(timestamp,severity,textPayload)" \
    --project=$PROJECT_ID || echo "⚠️ Erro ao obter logs"

echo ""
echo "3️⃣ Verificando status do serviço..."
echo "----------------------------------------"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="table(status.conditions[0].type,status.conditions[0].status,status.url)" || echo "⚠️ Erro ao obter status"

echo ""
echo "4️⃣ Verificando variáveis de ambiente críticas..."
echo "----------------------------------------"
echo "Variáveis necessárias:"
echo "  - SECRET_KEY"
echo "  - DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"
echo "  - DB_NAME"
echo "  - DB_USER"
echo "  - DB_PASSWORD"
echo "  - CLOUD_SQL_CONNECTION_NAME"
echo ""

# Verificar se as variáveis estão configuradas
ENV_VARS=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env)" 2>/dev/null || echo "")

if [ -z "$ENV_VARS" ]; then
    echo -e "${RED}❌ Não foi possível obter variáveis de ambiente${NC}"
else
    echo -e "${GREEN}✅ Variáveis de ambiente encontradas${NC}"
fi

echo ""
echo "5️⃣ Aplicando correções..."
echo "----------------------------------------"

# Verificar se SECRET_KEY está configurada
SECRET_KEY_SET=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='SECRET_KEY')].value)" 2>/dev/null || echo "")

if [ -z "$SECRET_KEY_SET" ]; then
    echo -e "${YELLOW}⚠️ SECRET_KEY não configurada. Configurando...${NC}"
    # Gerar uma nova SECRET_KEY
    NEW_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    
    echo "Atualizando serviço com SECRET_KEY..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "SECRET_KEY=$NEW_SECRET_KEY" \
        --quiet || echo "⚠️ Erro ao atualizar SECRET_KEY"
    
    echo -e "${GREEN}✅ SECRET_KEY configurada${NC}"
else
    echo -e "${GREEN}✅ SECRET_KEY já está configurada${NC}"
fi

# Verificar se DJANGO_SETTINGS_MODULE está configurado
SETTINGS_MODULE=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DJANGO_SETTINGS_MODULE')].value)" 2>/dev/null || echo "")

if [ -z "$SETTINGS_MODULE" ]; then
    echo -e "${YELLOW}⚠️ DJANGO_SETTINGS_MODULE não configurado. Configurando...${NC}"
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
        --quiet || echo "⚠️ Erro ao atualizar DJANGO_SETTINGS_MODULE"
    
    echo -e "${GREEN}✅ DJANGO_SETTINGS_MODULE configurado${NC}"
else
    echo -e "${GREEN}✅ DJANGO_SETTINGS_MODULE já está configurado: $SETTINGS_MODULE${NC}"
fi

# Verificar se DEBUG está configurado (deve ser False em produção)
DEBUG_VALUE=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DEBUG')].value)" 2>/dev/null || echo "")

if [ -z "$DEBUG_VALUE" ] || [ "$DEBUG_VALUE" != "False" ]; then
    echo -e "${YELLOW}⚠️ DEBUG não está configurado como False. Configurando...${NC}"
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "DEBUG=False" \
        --quiet || echo "⚠️ Erro ao atualizar DEBUG"
    
    echo -e "${GREEN}✅ DEBUG configurado como False${NC}"
else
    echo -e "${GREEN}✅ DEBUG já está configurado corretamente: $DEBUG_VALUE${NC}"
fi

echo ""
echo "6️⃣ Verificando conexão com Cloud SQL..."
echo "----------------------------------------"
CLOUD_SQL_CONN=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_CONN" ]; then
    echo -e "${YELLOW}⚠️ CLOUD_SQL_CONNECTION_NAME não configurado${NC}"
    echo "Configurando com valor padrão..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
        --quiet || echo "⚠️ Erro ao atualizar CLOUD_SQL_CONNECTION_NAME"
    
    echo -e "${GREEN}✅ CLOUD_SQL_CONNECTION_NAME configurado${NC}"
else
    echo -e "${GREEN}✅ CLOUD_SQL_CONNECTION_NAME configurado: $CLOUD_SQL_CONN${NC}"
fi

echo ""
echo "7️⃣ Aplicando migrações do banco de dados..."
echo "----------------------------------------"
echo "Criando job de migração..."

# Verificar se o job já existe
JOB_EXISTS=$(gcloud run jobs describe migrate-monpec --region=$REGION --format="value(metadata.name)" 2>/dev/null || echo "")

if [ -z "$JOB_EXISTS" ]; then
    echo "Criando job de migração..."
    # Usar --set-cloudsql-instances ao invés de --cloud-sql-instances
    gcloud run jobs create migrate-monpec \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --region=$REGION \
        --command python \
        --args "manage.py,migrate,--noinput" \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
        --set-cloudsql-instances=$CLOUD_SQL_CONN \
        --quiet || echo "⚠️ Erro ao criar job de migração"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Job de migração criado${NC}"
    else
        echo -e "${RED}❌ Erro ao criar job de migração${NC}"
    fi
else
    echo -e "${GREEN}✅ Job de migração já existe${NC}"
fi

echo "Executando migrações..."
gcloud run jobs execute migrate-monpec --region=$REGION --wait || echo "⚠️ Erro ao executar migrações"

echo ""
echo "8️⃣ Verificando ALLOWED_HOSTS..."
echo "----------------------------------------"
echo "O ALLOWED_HOSTS deve incluir o host do Cloud Run."
echo "Verificando URL do serviço..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}✅ URL do serviço: $SERVICE_URL${NC}"
    # Extrair host da URL
    SERVICE_HOST=$(echo $SERVICE_URL | sed 's|https\?://||' | sed 's|/.*||')
    echo "Host: $SERVICE_HOST"
    echo ""
    echo "⚠️ IMPORTANTE: Verifique se o ALLOWED_HOSTS em settings_gcp.py inclui:"
    echo "   - $SERVICE_HOST"
    echo "   - Ou use '*' para permitir todos os hosts"
else
    echo -e "${RED}❌ Não foi possível obter URL do serviço${NC}"
fi

echo ""
echo "9️⃣ Testando acesso ao serviço..."
echo "----------------------------------------"
if [ -n "$SERVICE_URL" ]; then
    echo "Fazendo requisição de teste para: $SERVICE_URL"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" || echo "000")
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
        echo -e "${GREEN}✅ Serviço respondendo (HTTP $HTTP_CODE)${NC}"
    elif [ "$HTTP_CODE" = "400" ]; then
        echo -e "${RED}❌ Erro 400 ainda presente${NC}"
        echo ""
        echo "Possíveis causas:"
        echo "  1. Variáveis de ambiente não configuradas corretamente"
        echo "  2. Migrações não aplicadas"
        echo "  3. Problema com ALLOWED_HOSTS"
        echo "  4. Problema com conexão ao banco de dados"
        echo ""
        echo "Verifique os logs para mais detalhes:"
        echo "  gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME\" --limit=100 --project=$PROJECT_ID"
    else
        echo -e "${YELLOW}⚠️ Serviço retornou HTTP $HTTP_CODE${NC}"
    fi
else
    echo -e "${RED}❌ Não foi possível testar o serviço (URL não disponível)${NC}"
fi

echo ""
echo "=========================================="
echo "✅ DIAGNÓSTICO CONCLUÍDO"
echo "=========================================="
echo ""
echo "📝 Próximos passos:"
echo "  1. Verifique os logs do serviço para mais detalhes"
echo "  2. Certifique-se de que todas as variáveis de ambiente estão configuradas"
echo "  3. Verifique se as migrações foram aplicadas com sucesso"
echo "  4. Teste o acesso ao serviço novamente"
echo ""
echo "🔗 URL do serviço: $SERVICE_URL"
echo ""

