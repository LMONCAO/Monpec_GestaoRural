# Deploy rápido apenas para atualizar landing page
$ErrorActionPreference = "Continue"

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host ""
Write-Host "🚀 DEPLOY RÁPIDO - ATUALIZAÇÃO LANDING PAGE" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Configurar projeto
gcloud config set project $PROJECT_ID | Out-Null

Write-Host "▶ Fazendo build da imagem..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_TAG --timeout=600s 2>&1 | Write-Host

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "▶ Fazendo deploy no Cloud Run..." -ForegroundColor Yellow

# Obter variáveis de ambiente existentes
$service = gcloud run services describe $SERVICE_NAME --region $REGION --format=json | ConvertFrom-Json

# Fazer deploy mantendo as configurações existentes
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --quiet 2>&1 | Write-Host

if ($LASTEXITCODE -eq 0) {
    $url = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1
    Write-Host ""
    Write-Host "✅ DEPLOY CONCLUÍDO!" -ForegroundColor Green
    Write-Host "🌐 URL: $url" -ForegroundColor Green
} else {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
}






