#!/bin/bash
# Script para verificar se as variáveis de ambiente estão corretas no job

JOB_NAME="migrate-monpec"
REGION="us-central1"

echo "========================================"
echo "  VERIFICAR CONFIGURAÇÃO DO JOB"
echo "========================================"
echo ""

echo "▶ Variáveis de ambiente do job:"
gcloud run jobs describe "$JOB_NAME" --region "$REGION" --format="yaml(spec.template.spec.containers[0].env)"

echo ""
echo "▶ Cloud SQL instances configuradas:"
gcloud run jobs describe "$JOB_NAME" --region "$REGION" --format="get(spec.template.spec.containers[0].env)" | grep CLOUD_SQL || echo "⚠ CLOUD_SQL_CONNECTION_NAME não encontrado!"

echo ""
echo "▶ Instâncias Cloud SQL conectadas:"
gcloud run jobs describe "$JOB_NAME" --region "$REGION" --format="value(spec.template.spec.containers[0].env)" | grep -i cloudsql || echo "⚠ Nenhuma instância Cloud SQL encontrada!"

echo ""











