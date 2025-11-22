# 🔄 Script para Executar Migrações do Django
# Execute este script após o deploy para configurar o banco de dados

Write-Host "🔄 MONPEC - Executar Migrações" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$DB_INSTANCE = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$DB_PASSWORD = "Monpec2025!"

# Obter connection name
$CONNECTION_NAME = gcloud sql instances describe $DB_INSTANCE --format="value(connectionName)"

Write-Host "📋 Executando migrações..." -ForegroundColor Yellow

# Criar job temporário para migrações
Write-Host "   Criando job de migração..." -ForegroundColor Yellow
gcloud run jobs create migrate `
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
    --region $REGION `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars `
        DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
        DB_NAME=$DB_NAME,`
        DB_USER=$DB_USER,`
        DB_PASSWORD=$DB_PASSWORD,`
        CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME `
    --command python `
    --args manage.py,migrate `
    --max-retries 1 `
    --task-timeout 600 `
    2>&1 | Out-Null

# Se o job já existe, deletar e recriar
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Job já existe. Deletando e recriando..." -ForegroundColor Yellow
    gcloud run jobs delete migrate --region $REGION --quiet 2>&1 | Out-Null
    gcloud run jobs create migrate `
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
        --region $REGION `
        --add-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars `
            DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,`
            DB_NAME=$DB_NAME,`
            DB_USER=$DB_USER,`
            DB_PASSWORD=$DB_PASSWORD,`
            CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME `
        --command python `
        --args manage.py,migrate `
        --max-retries 1 `
        --task-timeout 600
}

# Executar o job
Write-Host "   Executando migrações..." -ForegroundColor Yellow
gcloud run jobs execute migrate --region $REGION --wait

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migrações executadas com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 PRÓXIMO PASSO:" -ForegroundColor Yellow
    Write-Host "   Crie um superusuário para acessar o admin:" -ForegroundColor Cyan
    Write-Host "   .\CRIAR_SUPERUSUARIO.ps1" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ Erro ao executar migrações. Verifique os logs acima." -ForegroundColor Red
}

Write-Host ""
