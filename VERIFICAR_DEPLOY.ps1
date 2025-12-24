# Script para verificar o status do deploy

$ProjectId = "monpec-sistema-rural"
$Region = "us-central1"
$ServiceName = "monpec"
$gcloudPath = "C:\Users\lmonc\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICANDO STATUS DO DEPLOY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar serviço
Write-Host "Verificando serviço Cloud Run..." -ForegroundColor Yellow
$serviceUrl = & $gcloudPath run services describe $ServiceName --region $Region --format="value(status.url)" 2>&1

if ($serviceUrl -and $serviceUrl -notmatch "ERROR") {
    Write-Host "✅ Serviço ativo!" -ForegroundColor Green
    Write-Host "URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    
    # Verificar status
    $status = & $gcloudPath run services describe $ServiceName --region $Region --format="value(status.conditions[0].status)" 2>&1
    Write-Host "Status: $status" -ForegroundColor White
    Write-Host ""
    
    # Verificar últimas revisões
    Write-Host "Últimas revisões:" -ForegroundColor Yellow
    & $gcloudPath run revisions list --service $ServiceName --region $Region --limit 3
    Write-Host ""
    
    # Verificar logs recentes
    Write-Host "Logs recentes:" -ForegroundColor Yellow
    & $gcloudPath run services logs read $ServiceName --region $Region --limit 10
} else {
    Write-Host "⚠️  Serviço não encontrado ou ainda em deploy" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Verificando builds em andamento..." -ForegroundColor Yellow
    & $gcloudPath builds list --limit 3
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

















