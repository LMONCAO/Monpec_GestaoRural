# Verificar erro atual no Cloud Run
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"

gcloud config set project $PROJECT_ID

Write-Host "📋 Verificando erros recentes no Cloud Run..." -ForegroundColor Yellow

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" `
  --limit=10 `
  --format="value(timestamp,textPayload)" `
  --freshness=10m

Write-Host ""
Write-Host "✅ Verificação concluída!" -ForegroundColor Green

