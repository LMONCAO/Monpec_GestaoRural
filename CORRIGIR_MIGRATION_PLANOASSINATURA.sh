#!/bin/bash
# Corrigir migration que tenta criar tabela que já existe
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔧 Corrigindo migration de PlanoAssinatura"
echo "============================================================"
echo ""
echo "Problema: Tabela 'gestao_rural_planoassinatura' já existe"
echo "Solução: Identificar e marcar a migration como fake"
echo ""

# Primeiro, vamos identificar qual migration cria PlanoAssinatura
echo "📋 Identificando migration que cria PlanoAssinatura..."
gcloud run jobs delete identificar-migration --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create identificar-migration \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="sh" \
  --args="-c,cd /app && grep -r 'PlanoAssinatura\|planoassinatura' gestao_rural/migrations/*.py | grep -E '0035|0036|0037|0038|0039|0040|0041|0042|0043|0044' | head -5" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute identificar-migration --region=$REGION --wait
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=identificar-migration" --limit=20 --format="value(textPayload)" 2>/dev/null | tail -10

gcloud run jobs delete identificar-migration --region=$REGION --quiet 2>/dev/null || true

echo ""
echo "🔧 Aplicando migrations com tratamento de erros..."
echo ""

# Aplicar migrations uma por uma, marcando como fake se a tabela já existir
gcloud run jobs delete aplicar-migrations-com-fake --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create aplicar-migrations-com-fake \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.core.management import call_command;from django.db import connection;cursor=connection.cursor();print('Verificando tabelas existentes...');cursor.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'gestao_rural_%' ORDER BY table_name\");tabelas=[r[0] for r in cursor.fetchall()];print(f'Tabelas encontradas: {len(tabelas)}');if 'gestao_rural_planoassinatura' in tabelas:print('Tabela planoassinatura existe, marcando 0035 como fake...');call_command('migrate','gestao_rural','0035_assinaturas_stripe','--fake');print('Aplicando migrations restantes...');call_command('migrate','--noinput');print('✅ Concluído!')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=900

echo "⏱️  Executando..."
gcloud run jobs execute aplicar-migrations-com-fake --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations aplicadas!"
    echo ""
    echo "🔄 Fazendo deploy..."
    gcloud run deploy monpec \
      --region=$REGION \
      --image="$IMAGE_NAME" \
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
    echo ""
    echo "❌ Erro. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migrations-com-fake" --limit=50 --format="value(textPayload)" 2>/dev/null | tail -30
fi

gcloud run jobs delete aplicar-migrations-com-fake --region=$REGION --quiet 2>/dev/null || true

