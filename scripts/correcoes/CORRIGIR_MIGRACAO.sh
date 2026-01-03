#!/bin/bash
# Script para corrigir e executar a migração corretamente

JOB_NAME="migrate-monpec"
REGION="us-central1"  # ✅ CORRIGIDO
SERVICE_NAME="monpec"

echo "========================================"
echo "🔧 Corrigindo e Executando Migração"
echo "========================================"
echo ""

# 1. Verificar se o job existe
echo "1️⃣  Verificando job de migração..."
JOB_EXISTS=$(gcloud run jobs describe $JOB_NAME --region $REGION 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Job não encontrado. Criando..."
    PROJECT_ID=$(gcloud config get-value project)
    IMAGE="gcr.io/$PROJECT_ID/monpec:latest"
    
    gcloud run jobs create $JOB_NAME \
        --image $IMAGE \
        --region $REGION \
        --command python \
        --args "manage.py,migrate" \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
        --max-retries 3 \
        --task-timeout 600
    
    if [ $? -eq 0 ]; then
        echo "✅ Job criado"
    else
        echo "❌ Erro ao criar job"
        exit 1
    fi
else
    echo "✅ Job já existe"
fi
echo ""

# 2. Verificar variáveis do serviço
echo "2️⃣  Verificando variáveis do serviço principal..."
SERVICE_ENV=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null)

if [ -z "$SERVICE_ENV" ] || ! echo "$SERVICE_ENV" | grep -q "DB_HOST"; then
    echo "⚠️  Variáveis de banco de dados não configuradas no serviço"
    echo ""
    echo "Por favor, configure primeiro as variáveis de ambiente:"
    echo ""
    echo "gcloud run services update $SERVICE_NAME --region $REGION \\"
    echo "  --update-env-vars 'DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME'"
    echo ""
    read -p "Pressione Enter após configurar as variáveis..."
fi
echo ""

# 3. Copiar variáveis do serviço para o job
echo "3️⃣  Copiando variáveis de ambiente do serviço para o job..."
echo "Obtendo variáveis do serviço..."

# Extrair variáveis do serviço e atualizar o job
gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null | while IFS=',' read -r env_var; do
    if [[ "$env_var" == *"DB_"* ]] || [[ "$env_var" == *"SECRET_KEY"* ]] || [[ "$env_var" == *"DJANGO_SETTINGS_MODULE"* ]]; then
        echo "  Configurando: $env_var"
    fi
done

# Atualizar job com variáveis do serviço
echo "Atualizando job com variáveis do serviço..."
SERVICE_ENV_STR=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null)

if [ -n "$SERVICE_ENV_STR" ]; then
    # Filtrar apenas variáveis necessárias para migração
    DB_VARS=$(echo "$SERVICE_ENV_STR" | grep -oE "(DB_[^,]+|SECRET_KEY=[^,]+|DJANGO_SETTINGS_MODULE=[^,]+)" | tr '\n' ',' | sed 's/,$//')
    
    if [ -n "$DB_VARS" ]; then
        echo "Atualizando job com: $DB_VARS"
        gcloud run jobs update $JOB_NAME --region $REGION --update-env-vars "$DB_VARS" 2>/dev/null
        echo "✅ Variáveis atualizadas no job"
    else
        echo "⚠️  Variáveis de banco não encontradas no serviço"
        echo "Configure manualmente:"
        echo "gcloud run jobs update $JOB_NAME --region $REGION \\"
        echo "  --update-env-vars 'DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=SUA_SENHA,DB_HOST=/cloudsql/SEU_CONNECTION_NAME,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp'"
    fi
else
    echo "⚠️  Não foi possível obter variáveis do serviço"
fi
echo ""

# 4. Executar migração
echo "4️⃣  Executando migração..."
echo "Aguarde, isso pode levar alguns minutos..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ Migração executada com sucesso!"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "❌ Migração falhou"
    echo "========================================"
    echo ""
    echo "Verifique os logs:"
    echo "  gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --limit 50"
    echo ""
    echo "Ou execute o diagnóstico:"
    echo "  ./DIAGNOSTICAR_MIGRACAO.sh"
    echo ""
fi




























