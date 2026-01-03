# Aplicar migrações do banco de dados no Cloud Run
# Execute este script para aplicar as migrações e resolver o erro 500

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$INSTANCE_NAME = "monpec-db"
$JOB_NAME = "migrate-monpec"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Aplicando migrações do banco de dados" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Obter connection name
$CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)"
Write-Host "Connection name: $CONNECTION_NAME" -ForegroundColor Yellow
Write-Host ""

# Variáveis de ambiente
$ENV_VARS = "DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!SenhaSegura,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

# Criar ou atualizar job
Write-Host "Criando/atualizando job de migração..." -ForegroundColor Cyan
try {
    gcloud run jobs create $JOB_NAME `
        --image $IMAGE_NAME `
        --region $REGION `
        --set-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $ENV_VARS `
        --memory 2Gi `
        --cpu 1 `
        --max-retries 3 `
        --task-timeout 600 `
        --command python `
        --args "manage.py,migrate,--noinput" `
        --quiet 2>&1 | Out-Null
    Write-Host "✅ Job criado!" -ForegroundColor Green
} catch {
    Write-Host "Job já existe, atualizando..." -ForegroundColor Yellow
    gcloud run jobs update $JOB_NAME `
        --image $IMAGE_NAME `
        --region $REGION `
        --set-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $ENV_VARS `
        --quiet 2>&1 | Out-Null
}

Write-Host ""
Write-Host "Executando migrações (aguarde...)..." -ForegroundColor Cyan
gcloud run jobs execute $JOB_NAME --region $REGION --wait

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migrações aplicadas com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Teste o serviço agora:" -ForegroundColor Cyan
    Write-Host "https://monpec-fzzfjppzva-uc.a.run.app" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Erro ao aplicar migrações. Verifique os logs:" -ForegroundColor Red
    Write-Host "gcloud run jobs executions logs read $JOB_NAME --region $REGION" -ForegroundColor Yellow
}

Write-Host ""

















