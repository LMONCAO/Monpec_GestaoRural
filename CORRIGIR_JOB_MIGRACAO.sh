#!/bin/bash
# Script para corrigir e atualizar o job de migração com todas as configurações corretas

set -e

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
JOB_NAME="migrate-monpec"

# Variáveis de ambiente - usando aspas simples para evitar problemas com caracteres especiais
ENV_VARS="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY='0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_\$1ap4+4t',DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD='Django2025@',CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,PYTHONUNBUFFERED=1"

echo ""
echo "========================================"
echo "  CORRIGIR JOB DE MIGRAÇÃO"
echo "========================================"
echo ""

echo "▶ Atualizando job com configurações corretas..."
gcloud run jobs update "$JOB_NAME" \
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

echo "✓ Job atualizado"
echo ""

echo "▶ Verificando configuração do job..."
echo ""
echo "Variáveis de ambiente configuradas:"
gcloud run jobs describe "$JOB_NAME" --region "$REGION" --format="value(spec.template.spec.containers[0].env)" | tr ',' '\n' | grep -E "(DJANGO_SETTINGS_MODULE|DB_|CLOUD_SQL|SECRET_KEY)" || echo "Não encontrado"
echo ""

echo "Cloud SQL connections:"
gcloud run jobs describe "$JOB_NAME" --region "$REGION" --format="value(spec.template.spec.containers[0].env[?(@.name=='CLOUD_SQL_CONNECTION_NAME')].value)" || echo "Não encontrado"
echo ""

echo "▶ Executando migração..."
gcloud run jobs execute "$JOB_NAME" --region "$REGION" --wait

echo ""
echo "✓ Processo concluído"
echo ""




