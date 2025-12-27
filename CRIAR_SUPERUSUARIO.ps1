# Script para criar superusuário no Cloud Run

param(
    [string]$ServiceName = "monpec",
    [string]$Region = "us-central1",
    [string]$ProjectId = ""
)

Write-Host "👤 Criando superusuário..." -ForegroundColor Cyan
Write-Host ""

if (-not $ProjectId) {
    $ProjectId = gcloud config get-value project 2>$null
    if (-not $ProjectId) {
        Write-Host "❌ Erro: Nenhum projeto configurado!" -ForegroundColor Red
        exit 1
    }
}

$imageName = "gcr.io/$ProjectId/$ServiceName`:latest"

Write-Host "📋 Criando job para criar superusuário..." -ForegroundColor Yellow

# Criar job
gcloud run jobs create createsuperuser `
    --image $imageName `
    --region $Region `
    --command python `
    --args "manage.py,createsuperuser" `
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
    --set-env-vars="PYTHONUNBUFFERED=1" `
    --interactive `
    2>$null

Write-Host "✅ Job criado/verificado" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Executando criação de superusuário..." -ForegroundColor Yellow
Write-Host "   Você será solicitado a inserir os dados do usuário" -ForegroundColor Gray
Write-Host ""

gcloud run jobs execute createsuperuser --region $Region --wait

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Superusuário criado com sucesso!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erro ao criar superusuário!" -ForegroundColor Red
    exit 1
}









