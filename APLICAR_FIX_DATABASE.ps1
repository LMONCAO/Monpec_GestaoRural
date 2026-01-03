# Aplicar fix_database.py no Cloud Run
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔧 Criando estruturas faltantes no banco" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

gcloud run jobs delete fix-database --region=$REGION --quiet 2>$null

# Ler o arquivo fix_database.py e executar
$scriptContent = Get-Content "fix_database.py" -Raw

Write-Host "⏱️  Criando job..." -ForegroundColor Yellow

gcloud run jobs create fix-database `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --command="python" `
  --args="fix_database.py" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=300

Write-Host "⏱️  Executando (aguarde 1-2 minutos)..." -ForegroundColor Yellow
gcloud run jobs execute fix-database --region=$REGION --wait

# Ver logs
Write-Host ""
Write-Host "📋 Logs:" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=fix-database" `
  --limit=50 `
  --format="value(textPayload)" `
  --freshness=5m

# Limpar
gcloud run jobs delete fix-database --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green

