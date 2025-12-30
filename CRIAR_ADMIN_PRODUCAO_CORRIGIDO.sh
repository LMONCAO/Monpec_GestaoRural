#!/bin/bash
# Script CORRIGIDO para criar usuário admin no sistema web
# CORREÇÃO: Usa cd /app para garantir que manage.py seja encontrado

PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
DB_INSTANCE="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
DB_PASSWORD="L6171r12@@jjms"
CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${DB_INSTANCE}"

echo "============================================================"
echo "CRIAR USUARIO ADMINISTRADOR - SISTEMA WEB (PRODUCAO)"
echo "============================================================"
echo ""

# Configurar projeto
gcloud config set project $PROJECT_ID

# Detectar qual imagem usar
IMAGE_NAME="gcr.io/${PROJECT_ID}/sistema-rural:latest"

echo "🚀 Criando Cloud Run Job para criar usuário admin..."
echo "   Username: admin"
echo "   Email: admin@monpec.com.br"
echo ""

# Deletar job anterior se existir
gcloud run jobs delete criar-admin --region=$REGION --quiet 2>/dev/null || true

# CORREÇÃO: Usar sh -c com cd /app para garantir que manage.py seja encontrado
gcloud run jobs create criar-admin \
  --region=$REGION \
  --image="$IMAGE_NAME" \
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME" \
  --set-cloudsql-instances=$CLOUD_SQL_CONNECTION_NAME \
  --command="sh" \
  --args="-c,cd /app && python manage.py garantir_admin --username admin --email admin@monpec.com.br --senha L6171r12@@" \
  --max-retries=1 \
  --memory=2Gi \
  --cpu=2

if [ $? -ne 0 ]; then
    echo "❌ ERRO: Não foi possível criar o job."
    echo "💡 Tente verificar se a imagem existe:"
    echo "   gcloud container images list --repository=gcr.io/$PROJECT_ID"
    exit 1
fi

echo ""
echo "✅ Job criado! Executando..."
echo "⏱️  Aguarde 1-3 minutos..."
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
    echo "   Username: admin"
    echo "   Senha: L6171r12@@"
    echo ""
    echo "🌐 Acesse: https://monpec.com.br/login/"
    echo ""
else
    echo ""
    echo "❌ ERRO ao executar o job."
    echo "💡 Verifique os logs:"
    echo "   gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=criar-admin\" --limit=50"
    echo ""
    exit 1
fi

