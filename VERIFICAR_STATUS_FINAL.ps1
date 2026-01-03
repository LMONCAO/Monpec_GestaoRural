# Verificar status final do sistema
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Verificando status final do sistema" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se há erros recentes
Write-Host "🔍 Verificando erros recentes..." -ForegroundColor Yellow
$errors = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" `
  --limit=3 `
  --format="value(textPayload)" `
  --freshness=5m

if ($errors) {
    Write-Host "⚠️  Ainda há erros:" -ForegroundColor Yellow
    $errors | Select-Object -First 20
} else {
    Write-Host "✅ Nenhum erro encontrado nos últimos 5 minutos!" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🌐 URLs do sistema:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Cyan
Write-Host "Dashboard: https://monpec-29862706245.us-central1.run.app/dashboard/" -ForegroundColor Cyan
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Próximos passos:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acesse: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Yellow
Write-Host "2. Teste fazer login" -ForegroundColor Yellow
Write-Host "3. Se funcionar, o sistema está operacional! ✅" -ForegroundColor Green
Write-Host ""

