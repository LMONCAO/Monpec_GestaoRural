# Script PowerShell para Deploy no Google Cloud Run
# Execute este script no PowerShell

Write-Host "🚀 ==========================================" -ForegroundColor Cyan
Write-Host "   DEPLOY COMPLETO - MONPEC" -ForegroundColor Cyan
Write-Host "   Google Cloud Run" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "❌ Erro: gcloud CLI não está instalado!" -ForegroundColor Red
    Write-Host "   Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Obter projeto atual
$projectId = gcloud config get-value project 2>$null
if (-not $projectId) {
    Write-Host "❌ Erro: Nenhum projeto Google Cloud configurado!" -ForegroundColor Red
    Write-Host "   Execute: gcloud config set project SEU_PROJECT_ID" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Projeto: $projectId" -ForegroundColor Green
Write-Host ""

# Configurações
$serviceName = "monpec"
$region = "us-central1"
$imageName = "gcr.io/$projectId/$serviceName`:latest"

# Habilitar APIs
Write-Host "📋 Habilitando APIs necessárias..." -ForegroundColor Yellow
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
Write-Host "✅ APIs habilitadas" -ForegroundColor Green
Write-Host ""

# Verificar Dockerfile
if (-not (Test-Path "Dockerfile.prod")) {
    Write-Host "❌ Erro: Dockerfile.prod não encontrado!" -ForegroundColor Red
    exit 1
}

# Build da imagem
Write-Host "📦 Fazendo build da imagem Docker..." -ForegroundColor Yellow
Write-Host "   Isso pode levar alguns minutos..." -ForegroundColor Gray
gcloud builds submit --tag $imageName --timeout=1800s
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build concluído" -ForegroundColor Green
Write-Host ""

# Deploy no Cloud Run
Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $serviceName `
    --image $imageName `
    --region $region `
    --platform managed `
    --allow-unauthenticated `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
    --set-env-vars="PYTHONUNBUFFERED=1"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deploy concluído" -ForegroundColor Green
Write-Host ""

# Obter URL do serviço
$serviceUrl = gcloud run services describe $serviceName --region=$region --format="value(status.url)" 2>$null
Write-Host "🌐 URL do serviço: $serviceUrl" -ForegroundColor Cyan
Write-Host ""

# Aviso sobre variáveis de ambiente
Write-Host "⚠️  IMPORTANTE: Configure as variáveis de ambiente necessárias:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   gcloud run services update $serviceName \"
Write-Host "     --region=$region \"
Write-Host "     --update-env-vars=`"SECRET_KEY=SUA_SECRET_KEY_AQUI`" \"
Write-Host "     --update-env-vars=`"DEBUG=False`" \"
Write-Host "     --update-env-vars=`"DB_NAME=monpec_db`" \"
Write-Host "     --update-env-vars=`"DB_USER=monpec_user`" \"
Write-Host "     --update-env-vars=`"DB_PASSWORD=SUA_SENHA_DB`" \"
Write-Host "     --update-env-vars=`"CLOUD_SQL_CONNECTION_NAME=PROJECT_ID:REGION:INSTANCE_NAME`""
Write-Host ""
Write-Host "   Para ver todas as variáveis necessárias, consulte: GUIA_DEPLOY_RAPIDO.md" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ ==========================================" -ForegroundColor Green
Write-Host "   DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Acesse: $serviceUrl" -ForegroundColor Cyan
Write-Host ""
















