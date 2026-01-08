#!/bin/bash
# Script para criar superusuário admin com SEU EMAIL
# Execute no Google Cloud Shell: copie e cole todo este conteúdo

echo "============================================================"
echo "🔐 CRIAR SUPERUSUÁRIO ADMIN - COM SEU EMAIL"
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

# Credenciais do admin - ALTERE AQUI
USERNAME="admin"
EMAIL="l.moncaosilva@gmail.com"  # <-- SEU EMAIL
PASSWORD="L6171r12@@Monpec2025"  # <-- SUA SENHA (mínimo 12 caracteres)

# Detectar imagem
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

# Configurar projeto
echo "📋 Configurando projeto..."
gcloud config set project $PROJECT_ID

echo ""
echo "🚀 Criando usuário admin..."
echo "   Username: $USERNAME"
echo "   Email: $EMAIL"
echo "   ⏱️  Este processo pode levar 1-3 minutos..."
echo ""

# Verificar se senha tem pelo menos 12 caracteres
if [ ${#PASSWORD} -lt 12 ]; then
    echo "❌ ERRO: A senha deve ter no mínimo 12 caracteres!"
    echo "   Senha atual tem ${#PASSWORD} caracteres."
    exit 1
fi

# Deletar job anterior se existir
echo "🧹 Limpando jobs anteriores..."
gcloud run jobs delete criar-admin --region=$REGION --quiet 2>/dev/null || true

# Criar job
echo "📦 Criando Cloud Run Job..."
gcloud run jobs create criar-admin \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py garantir_admin --username $USERNAME --email $EMAIL --senha $PASSWORD --forcar" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

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
echo "⏱️  Aguarde 1-3 minutos (o processo está rodando)..."
echo ""

# Executar o job
gcloud run jobs execute criar-admin --region=$REGION --wait

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ SUCESSO! Usuário admin criado!"
    echo "============================================================"
    echo ""
    echo "📝 Credenciais para login:"
    echo "   Username: $USERNAME"
    echo "   Email: $EMAIL"
    echo "   Senha: $PASSWORD"
    echo ""
    echo "🌐 Acesse o sistema em:"
    echo "   https://monpec-fzzfjppzva-uc.a.run.app/login/"
    echo ""
    echo "💡 DICA: Você pode fazer login usando:"
    echo "   - Username: $USERNAME"
    echo "   - OU Email: $EMAIL"
    echo ""
    echo "🧹 Deseja remover o job temporário? (opcional)"
    echo "   Execute: gcloud run jobs delete criar-admin --region=$REGION"
    echo ""
else
    echo ""
    echo "❌ ERRO ao executar o job."
    echo ""
    echo "💡 Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=criar-admin\" --limit=50"
    echo ""
    exit 1
fi
