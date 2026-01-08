# Ver logs do erro 500 no dashboard
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando logs do erro 500 no dashboard" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Últimos 5 erros:" -ForegroundColor Yellow
Write-Host ""

$logs = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" `
  --limit=5 `
  --format="value(timestamp,textPayload)" `
  --freshness=5m

if ($logs) {
    $logs | Select-Object -First 50
} else {
    Write-Host "✅ Nenhum erro encontrado nos últimos 5 minutos" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📋 Stack trace completo:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$allLogs = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" `
  --limit=100 `
  --format="value(textPayload)" `
  --freshness=5m

$allLogs | Select-String -Pattern "Traceback|ProgrammingError|DoesNotExist|Exception|Error|dashboard" -Context 0,20 | Select-Object -First 80


