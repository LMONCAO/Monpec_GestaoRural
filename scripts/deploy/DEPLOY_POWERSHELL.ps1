# Script PowerShell para Deploy no Google Cloud Run
# Execute: .\DEPLOY_POWERSHELL.ps1

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY MONPEC - Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar senha do banco
Write-Host "🔧 Verificando senha do banco..." -ForegroundColor Yellow
gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Senha do banco verificada" -ForegroundColor Green
} else {
    Write-Host "⚠️ Aviso: Não foi possível atualizar senha do banco (pode ser normal)" -ForegroundColor Yellow
}

# 2. Configurar projeto
Write-Host ""
Write-Host "📋 Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao configurar projeto!" -ForegroundColor Red
    exit 1
}

# 3. Garantir openpyxl no requirements
Write-Host ""
Write-Host "📦 Verificando requirements..." -ForegroundColor Yellow
if (-not (Test-Path "requirements_producao.txt") -or (Select-String -Path "requirements_producao.txt" -Pattern "^openpyxl" -Quiet)) {
    Add-Content -Path "requirements_producao.txt" -Value "openpyxl>=3.1.5" -ErrorAction SilentlyContinue
    Write-Host "✅ openpyxl adicionado ao requirements" -ForegroundColor Green
}

# 4. Gerar timestamp
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

# 5. Build
Write-Host ""
Write-Host "🔨 Buildando imagem..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_TAG
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build concluído" -ForegroundColor Green

# 6. Deploy
Write-Host ""
Write-Host "🚀 Deployando..." -ForegroundColor Yellow
$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --region=$REGION `
    --platform managed `
    --allow-unauthenticated `
    --add-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" `
    --set-env-vars $ENV_VARS `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

# 7. Obter URL
Write-Host ""
Write-Host "✅✅✅ DEPLOY CONCLUÍDO! ✅✅✅" -ForegroundColor Green
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
Write-Host ""
Write-Host "🔗 URL do Serviço: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Credenciais para Login:" -ForegroundColor Yellow
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Senha: L6171r12@@" -ForegroundColor White
Write-Host ""


