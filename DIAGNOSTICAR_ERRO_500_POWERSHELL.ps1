# Diagnosticar erro 500 atual
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Diagnosticando erro 500 - Logs mais recentes" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Últimos 10 erros:" -ForegroundColor Yellow
Write-Host ""
$errors = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" `
  --limit=10 `
  --format="value(timestamp,textPayload)" `
  --freshness=10m

$errors | Select-Object -First 30

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📋 Stack trace completo do último erro:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$logs = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" `
  --limit=50 `
  --format="value(textPayload)" `
  --freshness=10m

$logs | Select-String -Pattern "Traceback|ProgrammingError|DoesNotExist|Exception" -Context 0,30 | Select-Object -First 50

