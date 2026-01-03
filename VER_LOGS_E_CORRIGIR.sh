#!/bin/bash
# Ver logs do job que falhou e corrigir
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "📋 LOGS DO JOB QUE FALHOU"
echo "============================================================"
echo ""

gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -25

echo ""
echo "============================================================"
echo "🔧 TENTANDO SOLUÇÃO ALTERNATIVA"
echo "============================================================"
echo ""

# Limpar job anterior
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true

# Tentar marcar a migration como fake de forma mais específica
echo "📦 Criando job com comando mais específico..."
gcloud run jobs create corrigir-migration \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,gestao_rural,0034_financeiro_reestruturado,--fake" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=600

echo "⏱️  Executando passo 1 (marcar como fake)..."
gcloud run jobs execute corrigir-migration --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo "✅ Migration marcada como fake!"
    echo ""
    echo "📦 Aplicando migrations restantes..."
    
    # Atualizar job para aplicar migrations restantes
    gcloud run jobs update corrigir-migration \
      --region=$REGION \
      --args="manage.py,migrate,--noinput" \
      --quiet
    
    gcloud run jobs execute corrigir-migration --region=$REGION --wait
    
    if [ $? -eq 0 ]; then
        echo "✅ Todas as migrations aplicadas!"
        echo ""
        echo "🔄 Fazendo deploy..."
        gcloud run deploy monpec \
          --region=$REGION \
          --image="$IMAGE_NAME \
          --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
          --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
          --memory=2Gi \
          --cpu=2 \
          --timeout=300 \
          --allow-unauthenticated \
          --quiet
        
        echo ""
        echo "✅ Pronto! Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
    else
        echo "❌ Erro ao aplicar migrations restantes"
        gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -15
    fi
else
    echo "❌ Erro ao marcar migration como fake"
    echo ""
    echo "📋 Logs detalhados:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=corrigir-migration" --limit=30 --format="table(timestamp,severity,textPayload)" 2>/dev/null | tail -20
fi

# Limpar
gcloud run jobs delete corrigir-migration --region=$REGION --quiet 2>/dev/null || true
