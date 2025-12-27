#!/bin/bash
# Solução alternativa: Usar --update-env-vars para cada variável separadamente
# Isso evita problemas com caracteres especiais em variáveis de ambiente

set -e

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
JOB_NAME="migrate-monpec"
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec:latest"

echo ""
echo "========================================"
echo "  ATUALIZAR JOB - MÉTODO ALTERNATIVO"
echo "========================================"
echo ""

echo "▶ Atualizando job usando --update-env-vars para cada variável..."
gcloud run jobs update "$JOB_NAME" \
    --image "$IMAGE_NAME" \
    --region "$REGION" \
    --update-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" \
    --update-env-vars "DEBUG=False" \
    --update-env-vars "SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t" \
    --update-env-vars "DB_NAME=monpec_db" \
    --update-env-vars "DB_USER=monpec_user" \
    --update-env-vars "DB_PASSWORD=Django2025@" \
    --update-env-vars "CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
    --update-env-vars "PYTHONUNBUFFERED=1" \
    --set-cloudsql-instances "monpec-sistema-rural:us-central1:monpec-db" \
    --memory 2Gi \
    --cpu 1 \
    --max-retries 3 \
    --task-timeout 600 \
    --command python \
    --args "manage.py,migrate,--noinput" \
    --quiet

echo "✓ Job atualizado"
echo ""

echo "▶ Verificando configuração..."
echo ""
echo "Variáveis de ambiente:"
gcloud run jobs describe "$JOB_NAME" --region "$REGION" --format="get(spec.template.spec.containers[0].env)" | grep -E "(name|value)" | head -20
echo ""

echo "Cloud SQL instances:"
gcloud run jobs describe "$JOB_NAME" --region "$REGION" --format="get(spec.template.spec.containers[0].env)" | grep -i cloud
echo ""

echo "▶ Executando migração..."
gcloud run jobs execute "$JOB_NAME" --region "$REGION" --wait

echo ""
echo "✓ Processo concluído!"
echo ""




