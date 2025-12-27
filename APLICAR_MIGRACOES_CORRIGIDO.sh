#!/bin/bash
# Script CORRIGIDO para aplicar migrações
# Verifica se o job já existe antes de criar

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="monpec"
REGION="us-central1"  # ✅ CORRIGIDO
IMAGE="gcr.io/$PROJECT_ID/monpec:latest"
JOB_NAME="migrate-monpec"

echo "========================================"
echo "🗄️  Aplicando Migrações do Django"
echo "========================================"
echo ""

# Verificar se o job já existe
echo "Verificando se o job já existe..."
EXISTS=$(gcloud run jobs describe $JOB_NAME --region $REGION 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Job já existe, pulando criação..."
else
    echo "Criando job de migração..."
    gcloud run jobs create $JOB_NAME \
        --image $IMAGE \
        --region $REGION \
        --command python \
        --args "manage.py,migrate" \
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
        --max-retries 3 \
        --task-timeout 600
    
    if [ $? -eq 0 ]; then
        echo "✅ Job criado com sucesso!"
    else
        echo "❌ Erro ao criar job"
        exit 1
    fi
fi

echo ""
echo "Executando migrações..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ Migrações aplicadas com sucesso!"
    echo "========================================"
else
    echo ""
    echo "⚠️  Erro ao executar migrações"
    echo "Verifique se as variáveis de ambiente estão configuradas"
fi
echo ""





















