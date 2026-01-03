#!/bin/bash
# Corrigir migration 0036 que está falhando
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 Verificando logs do erro na migration 0036"
echo "============================================================"
echo ""
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-mig-final" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -A 20 "0036\|DuplicateTable\|already exists" | tail -30

echo ""
echo "============================================================"
echo "🔧 Tentando marcar 0036 como fake também"
echo "============================================================"
echo ""

gcloud run jobs update aplicar-mig-final \
  --region=$REGION \
  --args="manage.py,migrate,gestao_rural,0036_ajusteorcamentocompra_orcamentocompramensal_and_more,--fake"

echo "⏱️  Executando..."
gcloud run jobs execute aplicar-mig-final --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration 0036 marcada como fake!"
    echo ""
    echo "🔄 Aplicando migrations restantes..."
    gcloud run jobs update aplicar-mig-final \
      --region=$REGION \
      --args="manage.py,migrate,--noinput"
    
    gcloud run jobs execute aplicar-mig-final --region=$REGION --wait
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Todas as migrations aplicadas!"
    else
        echo ""
        echo "❌ Ainda há erros. Verifique os logs acima."
    fi
else
    echo ""
    echo "❌ Erro ao marcar 0036 como fake. Verifique os logs."
fi

