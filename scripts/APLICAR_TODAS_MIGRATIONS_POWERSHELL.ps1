# Aplicar todas as migrations pendentes
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📦 Aplicando todas as migrations pendentes" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Deletar job anterior
gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>$null

# Criar job para aplicar todas as migrations
Write-Host "⏱️  Criando job..." -ForegroundColor Yellow
gcloud run jobs create aplicar-migrations `
  --region=$REGION `
  --image=$IMAGE_NAME `
  --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db" `
  --set-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
  --command="python" `
  --args="manage.py,migrate,--noinput" `
  --max-retries=1 `
  --memory=2Gi `
  --cpu=2 `
  --task-timeout=600

Write-Host "⏱️  Executando (aguarde 2-5 minutos)..." -ForegroundColor Yellow
gcloud run jobs execute aplicar-migrations --region=$REGION --wait

# Verificar logs se falhar
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Job falhou. Verificando logs..." -ForegroundColor Yellow
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-migrations" `
      --limit=30 `
      --format="value(textPayload)" `
      --freshness=10m | Select-Object -First 50
}

# Limpar
gcloud run jobs delete aplicar-migrations --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green


