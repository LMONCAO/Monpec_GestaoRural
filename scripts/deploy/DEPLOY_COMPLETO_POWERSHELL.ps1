# Script PowerShell para Deploy COMPLETO no Google Cloud Run
# Execute: .\DEPLOY_COMPLETO_POWERSHELL.ps1

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"
# SECRET_KEY para Django (use uma chave segura em produção)
$SECRET_KEY = "django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY COMPLETO MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar projeto
Write-Host "📋 Verificando projeto..." -ForegroundColor Yellow
$CURRENT_PROJECT = gcloud config get-value project 2>$null
if ($CURRENT_PROJECT -ne $PROJECT_ID) {
    Write-Host "   Configurando projeto para: $PROJECT_ID" -ForegroundColor Yellow
    gcloud config set project $PROJECT_ID
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao configurar projeto!" -ForegroundColor Red
        Write-Host "   Verifique se você tem permissões no projeto $PROJECT_ID" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "✅ Projeto já configurado: $PROJECT_ID" -ForegroundColor Green
}
Write-Host ""

# 2. Verificar senha do banco
Write-Host "🔧 Verificando senha do banco..." -ForegroundColor Yellow
gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Senha do banco verificada" -ForegroundColor Green
} else {
    Write-Host "⚠️ Aviso: Não foi possível atualizar senha do banco (pode ser normal)" -ForegroundColor Yellow
}
Write-Host ""

# 3. Garantir openpyxl no requirements
Write-Host "📦 Verificando requirements..." -ForegroundColor Yellow
if (-not (Test-Path "requirements_producao.txt")) {
    Write-Host "   Criando requirements_producao.txt..." -ForegroundColor Yellow
    New-Item -Path "requirements_producao.txt" -ItemType File -Force | Out-Null
}
$HAS_OPENPYXL = Select-String -Path "requirements_producao.txt" -Pattern "^openpyxl" -Quiet
if (-not $HAS_OPENPYXL) {
    Add-Content -Path "requirements_producao.txt" -Value "openpyxl>=3.1.5"
    Write-Host "✅ openpyxl adicionado ao requirements" -ForegroundColor Green
} else {
    Write-Host "✅ openpyxl já está no requirements" -ForegroundColor Green
}
Write-Host ""

# 4. Gerar timestamp
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

Write-Host "🔨 Buildando imagem Docker..." -ForegroundColor Yellow
Write-Host "   Tag: $IMAGE_TAG" -ForegroundColor Gray
Write-Host "   Isso pode levar 5-10 minutos..." -ForegroundColor Gray
Write-Host ""

gcloud builds submit --tag $IMAGE_TAG
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    Write-Host "   Verifique os logs acima para mais detalhes" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# 5. Deploy
Write-Host "🚀 Deployando no Cloud Run..." -ForegroundColor Yellow
Write-Host "   Isso pode levar 2-5 minutos..." -ForegroundColor Gray
Write-Host ""

$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --region=$REGION `
    --platform managed `
    --allow-unauthenticated `
    --add-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" `
    --set-env-vars $ENV_VARS `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600 `
    --min-instances=0 `
    --max-instances=10

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    Write-Host "   Verifique os logs acima para mais detalhes" -ForegroundColor Yellow
    exit 1
}

# 6. Obter URL
Write-Host ""
Write-Host "✅✅✅ DEPLOY CONCLUÍDO COM SUCESSO! ✅✅✅" -ForegroundColor Green
Write-Host ""

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>$null
if ($SERVICE_URL) {
    Write-Host "🔗 URL do Serviço:" -ForegroundColor Cyan
    Write-Host "   $SERVICE_URL" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Credenciais para Login:" -ForegroundColor Yellow
    Write-Host "   Username: admin" -ForegroundColor White
    Write-Host "   Senha: L6171r12@@" -ForegroundColor White
    Write-Host ""
    Write-Host "⏱️ Aguarde 1-2 minutos para o serviço inicializar completamente" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "⚠️ Não foi possível obter a URL do serviço" -ForegroundColor Yellow
    Write-Host "   Execute: gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'" -ForegroundColor Gray
}

Write-Host "========================================" -ForegroundColor Cyan

