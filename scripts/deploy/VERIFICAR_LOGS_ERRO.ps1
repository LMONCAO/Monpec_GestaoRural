# Script Rapido para Verificar Logs de Erro do Cloud Run

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

Write-Host "Verificando logs de erro do servico $SERVICE_NAME..." -ForegroundColor Yellow
Write-Host ""

gcloud logging read `
    "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" `
    --limit=30 `
    --format="table(timestamp,severity,textPayload)" `
    --project=$PROJECT_ID

Write-Host ""
Write-Host "Para ver todos os logs (incluindo INFO):" -ForegroundColor Gray
Write-Host "gcloud logging read `"resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME`" --limit=50 --project=$PROJECT_ID" -ForegroundColor White



