#!/bin/bash
# Script para carregar dados do banco no Google Cloud Run
# Execute no Google Cloud Shell: copie e cole todo este conteúdo

echo "============================================================"
echo "📊 CARREGAR DADOS DO BANCO - SISTEMA MONPEC"
echo "============================================================"
echo ""

# Configurações do projeto
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"

# Parâmetros do comando (AJUSTE AQUI CONFORME NECESSÁRIO)
FONTE="${1:-sqlite}"  # sqlite, postgresql, json, csv, sincronizar
CAMINHO="${2:-backup/db_backup.sqlite3}"  # Caminho do arquivo ou vazio para sincronizar
USUARIO_ID="${3:-1}"  # ID do usuário
SOBRESCREVER="${4:-}"  # --sobrescrever se desejar sobrescrever
DRY_RUN="${5:-}"  # --dry-run para testar

# Detectar imagem
IMAGE_NAME="gcr.io/${PROJECT_ID}/monpec:latest"

# Configurar projeto
echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "📊 Parâmetros:"
echo "   Fonte: $FONTE"
echo "   Caminho: $CAMINHO"
echo "   Usuário ID: $USUARIO_ID"
echo "   Sobrescrever: ${SOBRESCREVER:-Não}"
echo "   Dry Run: ${DRY_RUN:-Não}"
echo ""

# Construir comando
COMANDO_ARGS="carregar_dados_banco --fonte $FONTE"
if [ -n "$CAMINHO" ] && [ "$FONTE" != "sincronizar" ]; then
    COMANDO_ARGS="$COMANDO_ARGS --caminho $CAMINHO"
fi
if [ -n "$USUARIO_ID" ]; then
    COMANDO_ARGS="$COMANDO_ARGS --usuario-id $USUARIO_ID"
fi
if [ -n "$SOBRESCREVER" ]; then
    COMANDO_ARGS="$COMANDO_ARGS --sobrescrever"
fi
if [ -n "$DRY_RUN" ]; then
    COMANDO_ARGS="$COMANDO_ARGS --dry-run"
fi

echo "🚀 Executando: python manage.py $COMANDO_ARGS"
echo "⏱️  Este processo pode levar 2-5 minutos..."
echo ""

# Deletar job anterior se existir
echo "🧹 Limpando jobs anteriores..."
gcloud run jobs delete carregar-dados-banco --region=$REGION --quiet 2>/dev/null || true

# Criar job
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

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ ERRO: Não foi possível criar o job."
    echo ""
    echo "💡 Possíveis soluções:"
    echo "   1. Verifique se a imagem existe:"
    echo "      gcloud container images list --repository=gcr.io/$PROJECT_ID"
    echo ""
    echo "   2. Se a imagem tiver outro nome, altere a variável IMAGE_NAME no script"
    echo ""
    exit 1
fi

echo ""
echo "✅ Job criado! Executando..."
echo "⏱️  Aguarde 2-5 minutos (o processo está rodando)..."
echo ""

# Executar o job
gcloud run jobs execute carregar-dados-banco --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ SUCESSO! Dados carregados!"
    echo "============================================================"
    echo ""
    echo "🧹 Deseja remover o job temporário? (opcional)"
    echo "   Execute: gcloud run jobs delete carregar-dados-banco --region=$REGION"
    echo ""
else
    echo ""
    echo "❌ ERRO ao executar o job."
    echo ""
    echo "💡 Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=carregar-dados-banco\" --limit=50 --format=json"
    echo ""
    exit 1
fi


