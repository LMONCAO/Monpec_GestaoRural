#!/bin/bash
# Criar tabela UsuarioAtivo que está faltando
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
IMAGE_NAME="gcr.io/monpec-sistema-rural/sistema-rural:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔧 Criando tabela UsuarioAtivo"
echo "============================================================"
echo ""
echo "Problema: Tabela 'gestao_rural_usuarioativo' não existe"
echo "Solução: Aplicar migration 0081 que cria essa tabela"
echo ""

gcloud run jobs delete criar-usuarioativo --region=$REGION --quiet 2>/dev/null || true

# Primeiro, desmarcar a migration 0081 como fake
echo "📦 Passo 1: Desmarcando migration 0081 como fake..."
gcloud run jobs create criar-usuarioativo \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"DELETE FROM django_migrations WHERE app='gestao_rural' AND name='0081_add_usuario_ativo'\");print('✅ Migration 0081 desmarcada como fake')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute criar-usuarioativo --region=$REGION --wait

# Agora aplicar a migration 0081
echo ""
echo "📦 Passo 2: Aplicando migration 0081 para criar a tabela..."
gcloud run jobs update criar-usuarioativo \
  --region=$REGION \
  --args="manage.py,migrate,gestao_rural,0081_add_usuario_ativo" \
  --quiet

gcloud run jobs execute criar-usuarioativo --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tabela UsuarioAtivo criada!"
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
    echo "✅ Pronto! Teste: https://monpec-fzzfjppzva-uc.a.run.app/login/"
else
    echo ""
    echo "❌ Erro. Logs:"
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=criar-usuarioativo" --limit=30 --format="value(textPayload)" 2>/dev/null | tail -20
fi

gcloud run jobs delete criar-usuarioativo --region=$REGION --quiet 2>/dev/null || true

