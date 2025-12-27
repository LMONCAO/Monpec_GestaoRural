# Script para aplicar migrações do Django no Cloud Run

param(
    [string]$ServiceName = "monpec",
    [string]$Region = "us-central1",
    [string]$ProjectId = ""
)

Write-Host "📝 Aplicando migrações do Django..." -ForegroundColor Cyan
Write-Host ""

if (-not $ProjectId) {
    $ProjectId = gcloud config get-value project 2>$null
    if (-not $ProjectId) {
        Write-Host "❌ Erro: Nenhum projeto configurado!" -ForegroundColor Red
        exit 1
    }
}

$imageName = "gcr.io/$ProjectId/$ServiceName`:latest"

Write-Host "📋 Criando job de migração..." -ForegroundColor Yellow

# Criar job de migração
gcloud run jobs create migrate `
    --image $imageName `
    --region $Region `
    --command python `
    --args "manage.py,migrate" `
    --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp" `
    --set-env-vars="PYTHONUNBUFFERED=1" `
    2>$null

# Se o job já existe, continuar mesmo assim
Write-Host "✅ Job criado/verificado" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Executando migrações..." -ForegroundColor Yellow
gcloud run jobs execute migrate --region $Region --wait

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migrações aplicadas com sucesso!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erro ao aplicar migrações!" -ForegroundColor Red
    Write-Host "   Verifique os logs: gcloud run jobs executions describe EXECUTION_NAME --region=$Region" -ForegroundColor Yellow
    exit 1
}









