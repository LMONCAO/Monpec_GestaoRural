# 👤 Script para Criar Superusuário
# Execute este script para criar um usuário administrador

Write-Host "👤 MONPEC - Criar Superusuário" -ForegroundColor Cyan
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

Write-Host "📝 Você precisará inserir:" -ForegroundColor Yellow
Write-Host "   - Nome de usuário"
Write-Host "   - Email"
Write-Host "   - Senha (2x)"
Write-Host ""

$confirm = Read-Host "Deseja continuar? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔧 Criando job para criar superusuário..." -ForegroundColor Yellow

# Criar job temporário
gcloud run jobs create createsuperuser `
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
    --args manage.py,createsuperuser `
    --max-retries 1 `
    --task-timeout 600 `
    2>&1 | Out-Null

# Se o job já existe, deletar e recriar
if ($LASTEXITCODE -ne 0) {
    Write-Host "   Job já existe. Deletando e recriando..." -ForegroundColor Yellow
    gcloud run jobs delete createsuperuser --region $REGION --quiet 2>&1 | Out-Null
    gcloud run jobs create createsuperuser `
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
        --args manage.py,createsuperuser `
        --max-retries 1 `
        --task-timeout 600
}

Write-Host ""
Write-Host "⚠️  ATENÇÃO: Este comando será interativo." -ForegroundColor Yellow
Write-Host "   Você precisará inserir os dados do superusuário." -ForegroundColor Yellow
Write-Host "   O processo pode demorar alguns minutos para iniciar." -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Executar agora? (S/N)"
if ($confirm -ne "S" -and $confirm -ne "s") {
    Write-Host "Operação cancelada." -ForegroundColor Yellow
    exit 0
}

# Executar o job (será interativo)
Write-Host ""
Write-Host "🚀 Executando criação de superusuário..." -ForegroundColor Yellow
Write-Host "   Aguarde... o prompt aparecerá em breve." -ForegroundColor Yellow
Write-Host ""

gcloud run jobs execute createsuperuser --region $REGION

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Superusuário criado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Agora você pode acessar o admin do Django!" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Erro ao criar superusuário. Verifique os logs acima." -ForegroundColor Red
}

Write-Host ""


