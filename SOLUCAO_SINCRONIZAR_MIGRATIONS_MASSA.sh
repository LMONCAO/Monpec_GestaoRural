#!/bin/bash
# Solução: Sincronizar migrations em massa (marcar todas como fake)
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🛠️ SINCRONIZAÇÃO EM MASSA DE MIGRATIONS"
echo "============================================================"
echo ""
echo "Estratégia: Marcar TODAS as migrations de gestao_rural como fake"
echo "Isso sincroniza o histórico do Django com o banco atual"
echo ""

# Limpar job anterior
gcloud run jobs delete sincronizar-migrations --region=$REGION --quiet 2>/dev/null || true

echo "📦 Passo 1: Marcando TODAS as migrations de gestao_rural como fake..."
gcloud run jobs create sincronizar-migrations \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="manage.py,migrate,gestao_rural,--fake" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=600

echo "⏱️  Executando passo 1 (aguarde 2-3 minutos)..."
gcloud run jobs execute sincronizar-migrations --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Passo 1 concluído! Todas as migrations de gestao_rural marcadas como fake"
    echo ""
    echo "📦 Passo 2: Aplicando migrations de sistema (admin, sessions, etc)..."
    
    gcloud run jobs update sincronizar-migrations \
      --region=$REGION \
      --args="manage.py,migrate,--noinput" \
      --quiet
    
    echo "⏱️  Executando passo 2 (aguarde 1-2 minutos)..."
    gcloud run jobs execute sincronizar-migrations --region=$REGION --wait
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Passo 2 concluído!"
        echo ""
        echo "📋 Verificando estado final das migrations..."
        gcloud run jobs delete verificar-final --region=$REGION --quiet 2>/dev/null || true
        
        gcloud run jobs create verificar-final \
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
        
        gcloud run jobs execute verificar-final --region=$REGION --wait
        
        PENDENTES=$(gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-final" --limit=100 --format="value(textPayload)" 2>/dev/null | grep -E "\[ \]" | wc -l)
        echo ""
        echo "   Migrations pendentes: $PENDENTES"
        
        if [ "$PENDENTES" -eq 0 ]; then
            echo ""
            echo "✅ Todas as migrations estão aplicadas!"
        else
            echo ""
            echo "⚠️  Ainda há $PENDENTES migrations pendentes (podem ser de outras apps)"
        fi
        
        gcloud run jobs delete verificar-final --region=$REGION --quiet 2>/dev/null || true
        
        echo ""
        echo "🔄 Fazendo deploy do serviço..."
        gcloud run deploy monpec \
          --region=$REGION \
          --image="$IMAGE_NAME" \
          --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
          --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
          --memory=2Gi \
          --cpu=2 \
          --timeout=300 \
          --allow-unauthenticated \
          --quiet
        
        echo ""
        echo "============================================================"
        echo "✅ SINCRONIZAÇÃO CONCLUÍDA!"
        echo "============================================================"
        echo ""
        echo "⏱️  Aguarde 1-2 minutos e teste:"
        echo "🌐 https://monpec-fzzfjppzva-uc.a.run.app/login/"
        echo ""
        echo "💡 Se ainda houver erro 500, verifique os logs:"
        echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=monpec\" --limit=5 --format=\"value(textPayload)\""
    else
        echo ""
        echo "❌ Erro no passo 2. Logs:"
        gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=sincronizar-migrations" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
    fi
else
    echo ""
    echo "❌ Erro no passo 1. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=sincronizar-migrations" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
fi

# Limpar
gcloud run jobs delete sincronizar-migrations --region=$REGION --quiet 2>/dev/null || true

