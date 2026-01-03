# Verificar erro mais recente no Cloud Run
$PROJECT_ID = "monpec-sistema-rural"

gcloud config set project $PROJECT_ID

Write-Host "📋 Verificando erros mais recentes..." -ForegroundColor Yellow
Write-Host ""

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" `
  --limit=10 `
  --format="value(timestamp,textPayload)" `
  --freshness=15m `
  --order=desc

Write-Host ""
Write-Host "✅ Verificação concluída!" -ForegroundColor Green

