#!/bin/bash
# COMANDO ÚNICO PARA EXECUTAR NO GOOGLE CLOUD SHELL
# Copie e cole TUDO de uma vez no Cloud Shell
# 
# USO:
#   Para sincronizar dados existentes:
#     bash <(curl -s https://raw.githubusercontent.com/seu-repo/.../CARREGAR_DADOS_CLOUD_SHELL_COMANDO_UNICO.sh) sincronizar "" 1
#
#   Para importar de SQLite (se você tem o arquivo):
#     bash <(curl -s https://raw.githubusercontent.com/seu-repo/.../CARREGAR_DADOS_CLOUD_SHELL_COMANDO_UNICO.sh) sqlite "backup/db_backup.sqlite3" 1

# Configurações do projeto
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"

# Parâmetros
FONTE="${1:-sincronizar}"
CAMINHO="${2:-}"
USUARIO_ID="${3:-1}"

# Detectar imagem
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec:latest"

echo "============================================================"
echo "📊 CARREGAR DADOS DO BANCO - SISTEMA MONPEC"
echo "============================================================"
echo ""
echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "📊 Parâmetros:"
echo "   Fonte: $FONTE"
echo "   Caminho: ${CAMINHO:-N/A}"
echo "   Usuário ID: $USUARIO_ID"
echo ""

# Construir comando
COMANDO_ARGS="carregar_dados_banco --fonte $FONTE"
if [ -n "$CAMINHO" ] && [ "$FONTE" != "sincronizar" ]; then
    COMANDO_ARGS="$COMANDO_ARGS --caminho $CAMINHO"
fi
COMANDO_ARGS="$COMANDO_ARGS --usuario-id $USUARIO_ID"

echo "🚀 Executando: python manage.py $COMANDO_ARGS"
echo ""

# Limpar e criar job
gcloud run jobs delete carregar-dados-banco --region=$REGION --quiet 2>/dev/null || true

echo "📦 Criando Cloud Run Job..."
gcloud run jobs create carregar-dados-banco \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME,GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="python" \
  --args="manage.py,$COMANDO_ARGS" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=1800

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Job criado! Executando..."
    gcloud run jobs execute carregar-dados-banco --region=$REGION --wait
    echo ""
    echo "✅ Processo concluído!"
fi


