#!/bin/bash
# Rebuild e Deploy com nome de imagem correto
# Execute no Google Cloud Shell

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

gcloud config set project $PROJECT_ID

echo "============================================================"
echo "🔨 Rebuild da imagem Docker"
echo "============================================================"
echo ""

# Opção 1: Usar cloudbuild-config.yaml (cria monpec:latest)
echo "📦 Opção 1: Build usando cloudbuild-config.yaml..."
gcloud builds submit \
  --config=cloudbuild-config.yaml \
  --substitutions=_PROJECT_ID=$PROJECT_ID,_COMMIT_SHA=$(date +%Y%m%d%H%M%S) \
  --timeout=600s

# A imagem será: gcr.io/monpec-sistema-rural/monpec:latest
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec:latest"

echo ""
echo "✅ Build concluído!"
echo ""

# Criar tabela se não existir
echo "📦 Verificando/criando tabela UsuarioAtivo..."
gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>/dev/null || true

gcloud run jobs create criar-usuarioativo-final \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" \
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
  --command="python" \
  --args="-c,import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.db import connection;cursor=connection.cursor();cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')\");exists=cursor.fetchone()[0];print('Tabela existe:',exists);if not exists:print('Criando...');cursor.execute('''CREATE TABLE gestao_rural_usuarioativo (id BIGSERIAL NOT NULL PRIMARY KEY, nome_completo VARCHAR(255) NOT NULL, email VARCHAR(254) NOT NULL, telefone VARCHAR(20), primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), total_acessos INTEGER NOT NULL DEFAULT 0, ativo BOOLEAN NOT NULL DEFAULT true, criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), usuario_id BIGINT NOT NULL UNIQUE, CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED)''');cursor.execute(\"CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)\");cursor.execute(\"INSERT INTO django_migrations (app, name, applied) VALUES ('gestao_rural', '0081_add_usuario_ativo', NOW()) ON CONFLICT (app, name) DO NOTHING\");cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')\");exists=cursor.fetchone()[0];print('✅ Criada!' if exists else '❌ Erro')" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --task-timeout=300

gcloud run jobs execute criar-usuarioativo-final --region=$REGION --wait
gcloud run jobs delete criar-usuarioativo-final --region=$REGION --quiet 2>/dev/null || true

# Deploy
echo ""
echo "🚀 Fazendo deploy..."
gcloud run deploy $SERVICE_NAME \
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
echo "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/"


