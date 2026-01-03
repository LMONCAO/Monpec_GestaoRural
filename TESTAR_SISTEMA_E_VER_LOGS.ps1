# Testar sistema e ver logs de erro
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando erros recentes do sistema" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Últimos 5 erros:" -ForegroundColor Yellow
Write-Host ""

$errors = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" `
  --limit=5 `
  --format="value(timestamp,textPayload)" `
  --freshness=5m

if ($errors) {
    $errors | Select-Object -First 30
    Write-Host ""
    Write-Host "⚠️  Ainda há erros. Verificando detalhes..." -ForegroundColor Yellow
} else {
    Write-Host "✅ Nenhum erro encontrado nos últimos 5 minutos!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 O sistema pode estar funcionando!" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🌐 Teste o sistema:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Cyan
Write-Host "Dashboard: https://monpec-29862706245.us-central1.run.app/dashboard/" -ForegroundColor Cyan
Write-Host ""

