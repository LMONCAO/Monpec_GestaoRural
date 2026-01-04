# Script de Deploy Completo para Google Cloud Run (PowerShell)
# Uso: .\scripts\deploy_cloud_run.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Iniciando deploy do Monpec Gestão Rural no Google Cloud Run..." -ForegroundColor Green

# Variáveis (ajustar conforme necessário)
$PROJECT_ID = if ($env:GOOGLE_CLOUD_PROJECT) { $env:GOOGLE_CLOUD_PROJECT } else { "seu-project-id" }
$REGION = if ($env:REGION) { $env:REGION } else { "us-central1" }
$SERVICE_NAME = "monpec"
$INSTANCE_NAME = if ($env:CLOUD_SQL_INSTANCE) { $env:CLOUD_SQL_INSTANCE } else { "monpec-db" }

Write-Host "📋 Configuração:" -ForegroundColor Yellow
Write-Host "  Project ID: $PROJECT_ID"
Write-Host "  Region: $REGION"
Write-Host "  Service: $SERVICE_NAME"
Write-Host "  Cloud SQL Instance: $INSTANCE_NAME"
Write-Host ""

# Verificar se gcloud está instalado
try {
    gcloud --version | Out-Null
} catch {
    Write-Host "❌ Google Cloud SDK não está instalado!" -ForegroundColor Red
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Verificar se está autenticado
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authStatus) {
    Write-Host "⚠️ Não autenticado no Google Cloud. Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
}

# Definir projeto
Write-Host "✅ Definindo projeto: $PROJECT_ID" -ForegroundColor Green
gcloud config set project $PROJECT_ID

# Passo 1: Aplicar Migrations
Write-Host "📦 Passo 1: Aplicando migrations..." -ForegroundColor Green
$jobExists = gcloud run jobs describe migrate-db --region=$REGION 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Criando job de migrations..."
    gcloud run jobs create migrate-db `
        --image "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest" `
        --region $REGION `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
        --add-cloudsql-instances "$PROJECT_ID`:$REGION`:$INSTANCE_NAME" `
        --command python `
        --args "manage.py,migrate" `
        --memory 512Mi `
        --timeout 600 `
        --max-retries 1
} else {
    Write-Host "Job de migrations já existe. Atualizando..."
    gcloud run jobs update migrate-db `
        --image "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest" `
        --region $REGION `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
        --add-cloudsql-instances "$PROJECT_ID`:$REGION`:$INSTANCE_NAME" `
        --command python `
        --args "manage.py,migrate" `
        --memory 512Mi `
        --timeout 600
}

# Executar migrations
Write-Host "Executando migrations..."
gcloud run jobs execute migrate-db --region=$REGION --wait
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Erro ao executar migrations. Continuando com deploy..." -ForegroundColor Yellow
}

# Passo 2: Build da Imagem
Write-Host "📦 Passo 2: Fazendo build da imagem Docker..." -ForegroundColor Green
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}

# Passo 3: Deploy no Cloud Run
Write-Host "🚀 Passo 3: Fazendo deploy no Cloud Run..." -ForegroundColor Green
gcloud run deploy $SERVICE_NAME `
    --image "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest" `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
    --add-cloudsql-instances "$PROJECT_ID`:$REGION`:$INSTANCE_NAME" `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --port 8080

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

# Obter URL do serviço
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format 'value(status.url)'

Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "🌐 URL do serviço: $SERVICE_URL" -ForegroundColor Green

# Passo 4: Verificar Status
Write-Host "🔍 Passo 4: Verificando status..." -ForegroundColor Green
Start-Sleep -Seconds 5
gcloud run services describe $SERVICE_NAME --region=$REGION --format="table(status.conditions[0].type,status.conditions[0].status)"

Write-Host "✅ Deploy finalizado!" -ForegroundColor Green
Write-Host "📝 Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Verificar logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
Write-Host "  2. Testar site: curl $SERVICE_URL"
Write-Host "  3. Configurar domínio customizado se necessário"


