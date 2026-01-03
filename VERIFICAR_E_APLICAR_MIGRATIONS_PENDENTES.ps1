# Verificar e aplicar migrations pendentes
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🔍 Verificando migrations pendentes" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Passo 1: Verificar migrations pendentes
gcloud run jobs delete verificar-migrations --region=$REGION --quiet 2>$null

gcloud run jobs create verificar-migrations `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --command="python" `
  --args="manage.py,showmigrations,gestao_rural" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=300

Write-Host "⏱️  Verificando migrations pendentes..." -ForegroundColor Yellow
gcloud run jobs execute verificar-migrations --region=$REGION --wait

# Ver logs do job
Write-Host ""
Write-Host "📋 Logs do job:" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=verificar-migrations" `
  --limit=50 `
  --format="value(textPayload)" `
  --freshness=5m | Select-Object -First 100

# Passo 2: Aplicar todas as migrations
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📦 Aplicando todas as migrations" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>$null

gcloud run jobs create aplicar-todas-migrations `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --command="python" `
  --args="manage.py,migrate,--noinput" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=900

Write-Host "⏱️  Aplicando migrations (aguarde 3-5 minutos)..." -ForegroundColor Yellow
gcloud run jobs execute aplicar-todas-migrations --region=$REGION --wait

# Ver logs
Write-Host ""
Write-Host "📋 Logs da aplicação:" -ForegroundColor Yellow
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-todas-migrations" `
  --limit=100 `
  --format="value(textPayload)" `
  --freshness=10m | Select-Object -First 100

# Limpar
gcloud run jobs delete verificar-migrations --region=$REGION --quiet 2>$null
gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green

