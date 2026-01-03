# Ver logs corretamente
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando logs de erro" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Últimos 10 erros:" -ForegroundColor Yellow
Write-Host ""

# Comando corrigido - cada parâmetro em linha separada
gcloud logging read `
  "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" `
  --limit=10 `
  --format="value(timestamp,textPayload)" `
  --freshness=10m

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📋 Stack trace completo:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Ver logs completos
$logs = gcloud logging read `
  "resource.type=cloud_run_revision AND resource.labels.service_name=monpec" `
  --limit=50 `
  --format="value(textPayload)" `
  --freshness=10m

# Filtrar por erros
$logs | Select-String -Pattern "Traceback|ProgrammingError|DoesNotExist|Exception|Error" -Context 0,25

