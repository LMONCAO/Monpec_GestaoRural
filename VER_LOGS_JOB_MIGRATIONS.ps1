# Ver logs do job de migrations
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📋 Logs do job aplicar-todas-migrations" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$logs = gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-todas-migrations" `
  --limit=100 `
  --format="value(textPayload)" `
  --freshness=10m

if ($logs) {
    $logs | Select-Object -First 100
} else {
    Write-Host "⚠️  Nenhum log encontrado. Tentando buscar por execution..." -ForegroundColor Yellow
    
    # Buscar por execution recente
    $executions = gcloud run jobs executions list --job=aplicar-todas-migrations --region=us-central1 --limit=1 --format="value(name)"
    if ($executions) {
        $execName = $executions.Split('/')[-1]
        Write-Host "📋 Logs da execution: $execName" -ForegroundColor Yellow
        gcloud logging read "resource.type=cloud_run_job_execution AND resource.labels.job_name=aplicar-todas-migrations" `
          --limit=100 `
          --format="value(textPayload)" `
          --freshness=10m | Select-Object -First 100
    }
}

