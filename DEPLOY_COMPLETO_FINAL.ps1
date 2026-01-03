# Script PowerShell para Deploy Completo no Google Cloud Run
# Execute: .\DEPLOY_COMPLETO_FINAL.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY COMPLETO - MONPEC GCP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

# 1. Verificar ambiente
Write-Host "[1/7] Verificando ambiente..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    exit 1
}

try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "✅ Google Cloud SDK instalado" -ForegroundColor Green
} catch {
    Write-Host "❌ Google Cloud SDK não encontrado!" -ForegroundColor Red
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# 2. Aplicar migrations localmente (para verificar)
Write-Host "[2/7] Aplicando migrations locais..." -ForegroundColor Yellow
try {
    python manage.py migrate --noinput
    Write-Host "✅ Migrations aplicadas" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Aviso: $_" -ForegroundColor Yellow
}
Write-Host ""

# 3. Configurar projeto GCP
Write-Host "[3/7] Configurando projeto GCP..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Write-Host "✅ Projeto configurado: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# 4. Verificar autenticação
Write-Host "[4/7] Verificando autenticação GCP..." -ForegroundColor Yellow
$auth = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if ($auth) {
    Write-Host "✅ Autenticado como: $auth" -ForegroundColor Green
} else {
    Write-Host "⚠️  Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
}
Write-Host ""

# 5. Habilitar APIs
Write-Host "[5/7] Habilitando APIs necessárias..." -ForegroundColor Yellow
$APIS = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "sqladmin.googleapis.com"
)

foreach ($api in $APIS) {
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Host "✅ APIs habilitadas" -ForegroundColor Green
Write-Host ""

# 6. Build e Deploy
Write-Host "[6/7] Buildando e deployando no Cloud Run..." -ForegroundColor Yellow
Write-Host "⏱️  Isso pode levar 10-15 minutos..." -ForegroundColor Cyan

$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest"

# Build da imagem
Write-Host "  📦 Buildando imagem Docker..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_TAG 2>&1 | Tee-Object -Variable buildOutput

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    Write-Host $buildOutput
    exit 1
}
Write-Host "  ✅ Build concluído" -ForegroundColor Green

# Deploy no Cloud Run
Write-Host "  🚀 Deployando no Cloud Run..." -ForegroundColor Yellow

$ENV_VARS = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False"
)

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --region=$REGION `
    --platform managed `
    --allow-unauthenticated `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600 `
    --min-instances=1 `
    --max-instances=10 `
    --port=8080 `
    --set-env-vars ($ENV_VARS -join ",") 2>&1 | Tee-Object -Variable deployOutput

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    Write-Host $deployOutput
    exit 1
}
Write-Host "  ✅ Deploy concluído" -ForegroundColor Green
Write-Host ""

# 7. Obter URL
Write-Host "[7/7] Obtendo URL do serviço..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1

if ($SERVICE_URL) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 URL do serviço:" -ForegroundColor Yellow
    Write-Host "   $SERVICE_URL" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 Próximos passos:" -ForegroundColor Yellow
    Write-Host "1. Acesse a URL acima para testar" -ForegroundColor White
    Write-Host "2. Verifique os logs: gcloud run services logs read $SERVICE_NAME --region=$REGION" -ForegroundColor White
    Write-Host "3. Aplique migrations no banco de produção se necessário" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  Não foi possível obter a URL do serviço" -ForegroundColor Yellow
    Write-Host "Verifique manualmente no console do GCP" -ForegroundColor Yellow
}

