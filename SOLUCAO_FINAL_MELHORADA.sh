#!/bin/bash
# Solução FINAL melhorada com todas as correções
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔍 DIAGNÓSTICO E CORREÇÃO COMPLETA"
echo "============================================================"
echo ""

# 1. Ver logs da última revisão
echo "1️⃣ Verificando logs da última revisão..."
REVISION=$(gcloud run revisions list --service=monpec --region=$REGION --limit=1 --format="value(name)" 2>/dev/null | head -1)
if [ -n "$REVISION" ]; then
    echo "   Revisão: $REVISION"
    echo ""
    gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND resource.labels.revision_name=$REVISION" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -10
fi

echo ""
echo "2️⃣ Verificando migrations pendentes..."
gcloud run jobs delete verificar-mig --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create verificar-mig \
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

gcloud run jobs execute verificar-mig --region=$REGION --wait

PENDENTES=$(gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-mig" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | wc -l)
echo "   Migrations pendentes: $PENDENTES"

gcloud run jobs delete verificar-mig --region=$REGION --quiet 2>/dev/null || true

# 3. Aplicar migrations se necessário
if [ "$PENDENTES" -gt 0 ]; then
    echo ""
    echo "3️⃣ Aplicando migrations ($PENDENTES pendentes)..."
    gcloud run jobs delete aplicar-mig-final --region=$REGION --quiet 2>/dev/null || true
    
    gcloud run jobs create aplicar-mig-final \
      --region=$REGION \
      --image="$IMAGE_NAME" \
      --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
      --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
      --command="python" \
      --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;print('Marcando 0034 como fake...');call_command('migrate','gestao_rural','0034_financeiro_reestruturado','--fake');print('Marcando 0035 como fake...');call_command('migrate','gestao_rural','0035_assinaturas_stripe','--fake');print('Aplicando todas as migrations...');call_command('migrate','--noinput');print('✅ Migrations aplicadas!')" \
      --max-retries=1 \
      --memory=2Gi \
      --cpu=2 \
      --task-timeout=900
    
    echo "⏱️  Executando (aguarde 3-5 minutos)..."
    gcloud run jobs execute aplicar-mig-final --region=$REGION --wait
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Migrations aplicadas com sucesso!"
    else
        echo "   ⚠️ Houve problemas ao aplicar migrations"
        gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-mig-final" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
    fi
    
    gcloud run jobs delete aplicar-mig-final --region=$REGION --quiet 2>/dev/null || true
else
    echo ""
    echo "   ✅ Nenhuma migration pendente!"
fi

# 4. Deploy com --set-cloudsql-instances (não --add)
echo ""
echo "4️⃣ Fazendo deploy do serviço..."
gcloud run deploy monpec \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300 \
  --max-instances=10 \
  --allow-unauthenticated \
  --port=8080 \
  --quiet

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
    echo "💡 Se ainda houver erro 500, verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=monpec\" --limit=5 --format=\"value(textPayload)\""
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

