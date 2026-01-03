# Aplicar TODAS as migrations pendentes - Versão Definitiva
# Execute no PowerShell

$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec:latest"

gcloud config set project $PROJECT_ID

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📦 Aplicando TODAS as migrations pendentes" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Deletar jobs anteriores
gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>$null

# Criar job com timeout maior
Write-Host "⏱️  Criando job (timeout de 15 minutos)..." -ForegroundColor Yellow
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

Write-Host "⏱️  Executando (aguarde 3-5 minutos)..." -ForegroundColor Yellow
Write-Host "   Isso vai aplicar todas as migrations pendentes:" -ForegroundColor Gray
Write-Host "   - Migration 0077: mercadopago_customer_id" -ForegroundColor Gray
Write-Host "   - Migration 0081: UsuarioAtivo" -ForegroundColor Gray
Write-Host "   - Migration 0082: certificado_digital" -ForegroundColor Gray
Write-Host "   - E outras pendentes..." -ForegroundColor Gray
Write-Host ""

gcloud run jobs execute aplicar-todas-migrations --region=$REGION --wait

# Verificar resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migrations aplicadas com sucesso!" -ForegroundColor Green
    
    # Ver logs para confirmar
    Write-Host ""
    Write-Host "📋 Últimas linhas dos logs:" -ForegroundColor Yellow
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-todas-migrations" `
      --limit=30 `
      --format="value(textPayload)" `
      --freshness=10m | Select-Object -Last 20
} else {
    Write-Host ""
    Write-Host "⚠️  Job falhou. Verificando logs..." -ForegroundColor Yellow
    gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=aplicar-todas-migrations" `
      --limit=50 `
      --format="value(textPayload)" `
      --freshness=10m | Select-Object -First 50
}

# Limpar
gcloud run jobs delete aplicar-todas-migrations --region=$REGION --quiet 2>$null

Write-Host ""
Write-Host "✅ Pronto! Teste: https://monpec-29862706245.us-central1.run.app/login/" -ForegroundColor Green

