# Verificar status do deploy e testar sistema
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando status do serviço" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar status do serviço
Write-Host "📊 Status do serviço:" -ForegroundColor Yellow
gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url,status.latestReadyRevisionName,status.conditions[0].status)"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando logs recentes (últimos 5 minutos)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se há erros recentes
$errors = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" `
  --limit=5 `
  --format="value(textPayload)" `
  --freshness=5m

if ([string]::IsNullOrWhiteSpace($errors)) {
    Write-Host "✅ Nenhum erro encontrado nos últimos 5 minutos!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Erros encontrados:" -ForegroundColor Yellow
    Write-Host $errors
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🌐 URLs do sistema:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Cyan
Write-Host "Home: https://monpec-29862706245.us-central1.run.app/" -ForegroundColor Cyan
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Próximos passos:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acesse: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Yellow
Write-Host "2. Teste se a página de login carrega sem erro 500" -ForegroundColor Yellow
Write-Host "3. Se ainda houver erro, verifique os logs:" -ForegroundColor Yellow
Write-Host "   gcloud logging read `"resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR`" --limit=10 --format=`"value(textPayload)`" --freshness=5m" -ForegroundColor Gray
Write-Host ""


