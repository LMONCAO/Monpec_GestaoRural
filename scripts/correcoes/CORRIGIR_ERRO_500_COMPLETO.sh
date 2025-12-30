#!/bin/bash
# Script completo para corrigir erro 500 - Execute no Cloud Shell

set -e

echo "=========================================="
echo "🔧 CORREÇÃO COMPLETA - ERRO 500"
echo "=========================================="
echo ""

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
CLOUD_SQL_INSTANCE="monpec-sistema-rural:us-central1:monpec-db"

echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "1️⃣ Verificando logs de erro mais recentes..."
echo "----------------------------------------"
echo "Últimos 5 erros:"
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
    --limit=5 \
    --format="value(textPayload)" \
    --project=$PROJECT_ID | head -20

echo ""
echo "2️⃣ Verificando e configurando conexão Cloud SQL..."
echo "----------------------------------------"

# Verificar se a conexão Cloud SQL está configurada no serviço
CLOUD_SQL_CONNECTIONS=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].cloudSqlInstances)" 2>/dev/null || echo "")

if [ -z "$CLOUD_SQL_CONNECTIONS" ] || [[ ! "$CLOUD_SQL_CONNECTIONS" == *"$CLOUD_SQL_INSTANCE"* ]]; then
    echo "⚠️ Conexão Cloud SQL não está configurada. Adicionando..."
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --add-cloudsql-instances=$CLOUD_SQL_INSTANCE \
        --quiet
    
    if [ $? -eq 0 ]; then
        echo "✅ Conexão Cloud SQL adicionada ao serviço"
    else
        echo "❌ Erro ao adicionar conexão Cloud SQL"
        exit 1
    fi
else
    echo "✅ Conexão Cloud SQL já está configurada: $CLOUD_SQL_CONNECTIONS"
fi

echo ""
echo "3️⃣ Verificando e configurando CLOUD_SQL_CONNECTION_NAME..."
echo "----------------------------------------"
CURRENT_CLOUD_SQL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" 2>/dev/null || echo "")

if [ -z "$CURRENT_CLOUD_SQL" ] || [ "$CURRENT_CLOUD_SQL" != "$CLOUD_SQL_INSTANCE" ]; then
    echo "⚠️ CLOUD_SQL_CONNECTION_NAME não está configurado corretamente"
    echo "   Valor atual: '$CURRENT_CLOUD_SQL'"
    echo "   Configurando: '$CLOUD_SQL_INSTANCE'"
    
    gcloud run services update $SERVICE_NAME \
        --region=$REGION \
        --update-env-vars "CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_INSTANCE" \
        --quiet
    
    if [ $? -eq 0 ]; then
        echo "✅ CLOUD_SQL_CONNECTION_NAME configurado"
    else
        echo "❌ Erro ao configurar CLOUD_SQL_CONNECTION_NAME"
        exit 1
    fi
else
    echo "✅ CLOUD_SQL_CONNECTION_NAME já está configurado: $CURRENT_CLOUD_SQL"
fi

echo ""
echo "4️⃣ Verificando variáveis de ambiente do banco de dados..."
echo "----------------------------------------"
DB_NAME=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_NAME')].value)" 2>/dev/null || echo "")

DB_USER=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_USER')].value)" 2>/dev/null || echo "")

DB_PASSWORD=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(spec.template.spec.containers[0].env[?(@.name=='DB_PASSWORD')].value)" 2>/dev/null || echo "")

echo "DB_NAME: ${DB_NAME:-'NÃO CONFIGURADO (usará padrão: monpec_db)'}"
echo "DB_USER: ${DB_USER:-'NÃO CONFIGURADO (usará padrão: monpec_user)'}"
echo "DB_PASSWORD: ${DB_PASSWORD:+'***CONFIGURADO***'}${DB_PASSWORD:-'NÃO CONFIGURADO - ⚠️ NECESSÁRIO!'}"

if [ -z "$DB_PASSWORD" ]; then
    echo ""
    echo "⚠️ ATENÇÃO: DB_PASSWORD não está configurado!"
    echo "   Configure a senha do banco de dados:"
    echo "   gcloud run services update $SERVICE_NAME \\"
    echo "       --region=$REGION \\"
    echo "       --update-env-vars 'DB_PASSWORD=SUA_SENHA_AQUI'"
    echo ""
    echo "   Se não souber a senha, você pode resetá-la no Cloud SQL:"
    echo "   gcloud sql users set-password monpec_user --instance=monpec-db --password=NOVA_SENHA"
fi

echo ""
echo "5️⃣ Verificando instância do Cloud SQL..."
echo "----------------------------------------"
SQL_STATE=$(gcloud sql instances describe monpec-db --format="value(state)" 2>/dev/null || echo "NOT_FOUND")

if [ "$SQL_STATE" = "NOT_FOUND" ]; then
    echo "❌ Instância do Cloud SQL 'monpec-db' não encontrada!"
    echo "   Verifique se a instância existe e está no projeto correto"
elif [ "$SQL_STATE" != "RUNNABLE" ]; then
    echo "⚠️ Instância do Cloud SQL está no estado: $SQL_STATE"
    echo "   Estado esperado: RUNNABLE"
else
    echo "✅ Instância do Cloud SQL está rodando (RUNNABLE)"
    SQL_CONNECTION=$(gcloud sql instances describe monpec-db --format="value(connectionName)" 2>/dev/null)
    echo "   Connection Name: $SQL_CONNECTION"
fi

echo ""
echo "6️⃣ Verificando todas as variáveis de ambiente..."
echo "----------------------------------------"
echo "Variáveis configuradas:"
gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="table(spec.template.spec.containers[0].env.name,spec.template.spec.containers[0].env.value)" | grep -E "(SECRET_KEY|DJANGO_SETTINGS_MODULE|DEBUG|CLOUD_SQL|DB_)" || echo "Nenhuma variável relevante encontrada"

echo ""
echo "7️⃣ Aguardando atualização do serviço..."
echo "----------------------------------------"
echo "Aguardando 20 segundos para o serviço atualizar..."
sleep 20

echo ""
echo "8️⃣ Testando acesso ao serviço..."
echo "----------------------------------------"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION \
    --format="value(status.url)")

echo "URL: $SERVICE_URL"
echo "Fazendo requisição de teste..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL" || echo "000")
echo "HTTP Status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Serviço respondendo corretamente!"
elif [ "$HTTP_CODE" = "500" ]; then
    echo "❌ Erro 500 ainda presente"
    echo ""
    echo "Verificando logs de erro mais detalhados..."
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" \
        --limit=3 \
        --format="value(textPayload)" \
        --project=$PROJECT_ID | head -40
    echo ""
    echo "💡 Possíveis causas:"
    echo "   1. DB_PASSWORD não configurado"
    echo "   2. Credenciais do banco incorretas"
    echo "   3. Banco de dados não existe ou não está acessível"
    echo "   4. Migrações não aplicadas"
elif [ "$HTTP_CODE" = "400" ]; then
    echo "⚠️ Erro 400 ainda presente (ALLOWED_HOSTS)"
    echo "   Faça um novo deploy com as correções do código"
else
    echo "⚠️ Serviço retornou HTTP $HTTP_CODE"
fi

echo ""
echo "=========================================="
echo "✅ DIAGNÓSTICO CONCLUÍDO"
echo "=========================================="
echo ""
echo "📝 Resumo:"
echo "  - Conexão Cloud SQL: $([ -n "$CLOUD_SQL_CONNECTIONS" ] && echo "✅ Configurada" || echo "❌ Não configurada")"
echo "  - CLOUD_SQL_CONNECTION_NAME: $([ -n "$CURRENT_CLOUD_SQL" ] && echo "✅ $CURRENT_CLOUD_SQL" || echo "❌ Não configurado")"
echo "  - DB_PASSWORD: $([ -n "$DB_PASSWORD" ] && echo "✅ Configurado" || echo "❌ NÃO CONFIGURADO")"
echo "  - Status HTTP: $HTTP_CODE"
echo ""
echo "🔗 URL do serviço: $SERVICE_URL"
echo ""
if [ -z "$DB_PASSWORD" ]; then
    echo "⚠️ AÇÃO NECESSÁRIA: Configure DB_PASSWORD antes de continuar!"
fi
echo ""





