#!/bin/bash
set -e

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Django2025@,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

echo ""
echo "========================================"
echo "  REBUILD E DEPLOY - SISTEMA MONPEC"
echo "========================================"
echo ""

echo "▶ Configurando projeto..."
gcloud config set project "$PROJECT_ID" --quiet
echo "✓ Projeto configurado"
echo ""

echo "▶ Fazendo build da imagem Docker (10-15 minutos)..."
echo "  Isso garante que todas as dependências sejam instaladas corretamente"
gcloud builds submit --tag "$IMAGE_NAME:latest" --timeout=20m
echo "✓ Build concluído"
echo ""

echo "▶ Fazendo deploy no Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_NAME:latest" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "$ENV_VARS" \
    --add-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 1 \
    --port 8080 \
    --quiet
echo "✓ Deploy concluído"
echo ""

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" 2>/dev/null)
echo "✓ URL do serviço: $SERVICE_URL"
echo ""

echo "▶ Aplicando migrações..."
JOB_NAME="migrate-monpec"

if gcloud run jobs describe "$JOB_NAME" --region="$REGION" &>/dev/null; then
    echo "  Atualizando job de migração com nova imagem..."
    gcloud run jobs update "$JOB_NAME" \
        --image "$IMAGE_NAME:latest" \
        --region "$REGION" \
        --set-env-vars "$ENV_VARS" \
        --set-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" \
        --memory 2Gi \
        --cpu 1 \
        --max-retries 3 \
        --task-timeout 600 \
        --quiet
    
    echo "  Executando migrações..."
    gcloud run jobs execute "$JOB_NAME" --region="$REGION" --wait
else
    echo "  Criando job de migração..."
    gcloud run jobs create "$JOB_NAME" \
        --image "$IMAGE_NAME:latest" \
        --region "$REGION" \
        --set-env-vars "$ENV_VARS" \
        --set-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" \
        --memory 2Gi \
        --cpu 1 \
        --max-retries 3 \
        --task-timeout 600 \
        --command python \
        --args "manage.py,migrate,--noinput" \
        --quiet
    gcloud run jobs execute "$JOB_NAME" --region="$REGION" --wait
fi
echo "✓ Migrações aplicadas"
echo ""

echo "========================================"
echo "✓ REBUILD E DEPLOY CONCLUÍDOS!"
echo "========================================"
echo ""
echo "URL do serviço: $SERVICE_URL"
echo ""
echo "Ver logs: gcloud run services logs read $SERVICE_NAME --region=$REGION --limit=50"
echo ""

