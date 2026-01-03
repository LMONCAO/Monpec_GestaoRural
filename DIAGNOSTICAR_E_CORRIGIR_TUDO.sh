#!/bin/bash
# Script completo para diagnosticar e corrigir todos os problemas
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔍 DIAGNÓSTICO COMPLETO"
echo "============================================================"
echo ""

# 1. Ver logs da última revisão
echo "1️⃣ Verificando logs da última revisão..."
REVISION=$(gcloud run revisions list --service=monpec --region=$REGION --limit=1 --format="value(name)" 2>/dev/null | head -1)
if [ -n "$REVISION" ]; then
    echo "   Revisão: $REVISION"
    echo ""
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND resource.labels.revision_name=$REVISION" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -15
fi

echo ""
echo "2️⃣ Verificando estado das migrations..."
gcloud run jobs delete verificar-migrations-diagnostico --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create verificar-migrations-diagnostico \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,showmigrations,--list" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute verificar-migrations-diagnostico --region=$REGION --wait

echo ""
echo "   Migrations pendentes:"
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-migrations-diagnostico" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | wc -l | xargs -I {} echo "   Total: {} migrations pendentes"

PENDENTES=$(gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-migrations-diagnostico" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | wc -l)

gcloud run jobs delete verificar-migrations-diagnostico --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "============================================================"
echo "🔧 APLICANDO CORREÇÕES"
echo "============================================================"
echo ""

if [ "$PENDENTES" -gt 0 ]; then
    echo "📦 Aplicando migrations pendentes..."
    gcloud run jobs delete aplicar-todas-migrations-final --region=$REGION --quiet 2>/dev/null || true
    
    gcloud run jobs create aplicar-todas-migrations-final \
      --region=$REGION \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="python" \
      --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;print('Marcando 0034 e 0035 como fake...');call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');call_command('migrate','gestao_rural','0035_assinaturas_stripe','--fake');print('Aplicando todas as migrations...');call_command('migrate','--noinput');print('✅ Concluído!')" \
      --max-retries=1 \
      --memory=2Gi \
      --cpu=2 \
      --task-timeout=900
    
    echo "⏱️  Executando (aguarde 3-5 minutos)..."
    gcloud run jobs execute aplicar-todas-migrations-final --region=$REGION --wait
    
    gcloud run jobs delete aplicar-todas-migrations-final --region=$REGION --quiet 2>/dev/null || true
fi

echo ""
echo "============================================================"
echo "🔄 FAZENDO DEPLOY"
echo "============================================================"
echo ""

gcloud run deploy monpec \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --allow-unauthenticated \
  --port=8080

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ DEPLOY CONCLUÍDO!"
    echo "============================================================"
    echo ""
    echo "⏱️  Aguarde 1-2 minutos para o serviço inicializar..."
    echo ""
    echo "🌐 Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
    echo ""
else
    echo ""
    echo "❌ Deploy falhou. Verificando logs..."
    REVISION=$(gcloud run revisions list --service=monpec --region=$REGION --limit=1 --format="value(name)" 2>/dev/null | head -1)
    if [ -n "$REVISION" ]; then
        echo ""
        echo "📋 Logs da revisão $REVISION:"
        gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND resource.labels.revision_name=$REVISION" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
    fi
fi

