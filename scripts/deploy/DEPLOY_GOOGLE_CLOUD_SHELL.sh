#!/bin/bash
# 🚀 DEPLOY COMPLETO AUTOMÁTICO - Para executar no Google Cloud Shell
# Cole e cole este script no Cloud Shell: https://shell.cloud.google.com

set -e  # Parar em caso de erro

PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"
DB_NAME="monpec_db"
DB_USER="monpec_user"
IMAGE_NAME="gcr.io/$PROJECT_ID/monpec"
DOMAIN="monpec.com.br"
WWW_DOMAIN="www.monpec.com.br"

# Senhas (ALTERE EM PRODUÇÃO!)
DB_PASSWORD="Monpec2025!SenhaSegura"
SECRET_KEY="django-insecure-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

echo "========================================"
echo "🚀 DEPLOY COMPLETO AUTOMÁTICO - MONPEC"
echo "========================================"
echo ""

# Configurar projeto
echo "Configurando projeto..."
gcloud config set project $PROJECT_ID

# Habilitar APIs
echo "Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable sql-component.googleapis.com --quiet
echo "✅ APIs habilitadas!"
echo ""

# Verificar/Criar instância Cloud SQL
echo "Verificando instância Cloud SQL..."
if gcloud sql instances describe $INSTANCE_NAME &>/dev/null; then
    echo "✅ Instância Cloud SQL já existe"
else
    echo "Criando instância Cloud SQL..."
    gcloud sql instances create $INSTANCE_NAME \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=$DB_PASSWORD \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase \
        --backup-start-time=03:00 \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=4 \
        --quiet
    echo "✅ Instância Cloud SQL criada!"
fi

CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
echo "Connection name: $CONNECTION_NAME"

# Criar banco de dados
echo "Criando banco de dados..."
gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME --quiet 2>&1 || echo "Banco já existe"
gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD --quiet 2>&1 || echo "Usuário já existe"
echo "✅ Banco de dados configurado!"
echo ""

# Fazer upload do código para Cloud Shell
echo "Clonando repositório ou preparando código..."
# Se você tem um repositório Git:
# git clone SEU_REPOSITORIO
# cd SEU_REPOSITORIO
# OU faça upload manual dos arquivos

# Build da imagem
echo "Fazendo build da imagem Docker (5-10 minutos)..."
gcloud builds submit --tag $IMAGE_NAME --timeout=600s
echo "✅ Imagem Docker criada!"
echo ""

# Deploy no Cloud Run
echo "Fazendo deploy no Cloud Run..."
ENV_VARS="DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,PORT=8080"

gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars $ENV_VARS \
    --memory 2Gi \
    --cpu 2 \
    --timeout 600 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080 \
    --quiet

SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
echo "✅ Deploy concluído!"
echo "URL do serviço: $SERVICE_URL"
echo ""

# Aplicar migrações
echo "Aplicando migrações..."
JOB_NAME="migrate-monpec"
gcloud run jobs create $JOB_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --set-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars $ENV_VARS \
    --memory 2Gi \
    --cpu 1 \
    --max-retries 3 \
    --task-timeout 600 \
    --command python \
    --args "manage.py,migrate,--noinput" \
    --quiet 2>&1 || echo "Job já existe, atualizando..."

gcloud run jobs update $JOB_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --set-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars $ENV_VARS \
    --quiet 2>&1 || true

gcloud run jobs execute $JOB_NAME --region $REGION --wait
echo "✅ Migrações aplicadas!"
echo ""

# Collectstatic
echo "Coletando arquivos estáticos..."
STATIC_JOB_NAME="collectstatic-monpec"
gcloud run jobs create $STATIC_JOB_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --set-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars $ENV_VARS \
    --memory 2Gi \
    --cpu 1 \
    --max-retries 3 \
    --task-timeout 600 \
    --command python \
    --args "manage.py,collectstatic,--noinput" \
    --quiet 2>&1 || echo "Job já existe, atualizando..."

gcloud run jobs update $STATIC_JOB_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --set-cloudsql-instances $CONNECTION_NAME \
    --set-env-vars $ENV_VARS \
    --quiet 2>&1 || true

gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait
echo "✅ Arquivos estáticos coletados!"
echo ""

# Configurar domínio
echo "Configurando domínio..."
gcloud run domain-mappings create --service $SERVICE_NAME --domain $DOMAIN --region $REGION --quiet 2>&1 || echo "Domain mapping já existe"
gcloud run domain-mappings create --service $SERVICE_NAME --domain $WWW_DOMAIN --region $REGION --quiet 2>&1 || echo "Domain mapping já existe"

echo "✅ Domain mappings criados!"
echo "Registros DNS:"
gcloud run domain-mappings describe $DOMAIN --region $REGION --format="table(status.resourceRecords)"
echo ""

# Resumo final
echo "========================================"
echo "✅ DEPLOY COMPLETO CONCLUÍDO!"
echo "========================================"
echo ""
echo "🌐 URLs:"
echo "  • Cloud Run: $SERVICE_URL"
echo "  • Domínio: https://$DOMAIN (após configurar DNS)"
echo "  • WWW: https://$WWW_DOMAIN (após configurar DNS)"
echo ""
echo "📝 Próximos passos:"
echo "1. Configure os registros DNS no seu provedor de domínio"
echo "2. Aguarde a propagação DNS (5-30 minutos)"
echo "3. Acesse: $SERVICE_URL"
echo ""
echo "🎉 Tudo pronto!"

















