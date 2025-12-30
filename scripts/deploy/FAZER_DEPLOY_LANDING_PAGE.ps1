# 🚀 DEPLOY ATUALIZAÇÃO LANDING PAGE - MONPEC
# Script para fazer deploy apenas das alterações do template

$ErrorActionPreference = "Stop"

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

Write-Host ""
Write-Host "🚀 DEPLOY ATUALIZAÇÃO LANDING PAGE - MONPEC" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar gcloud
try { 
    gcloud --version | Out-Null 
    Write-Host "✅ gcloud CLI encontrado" -ForegroundColor Green
} catch { 
    Write-Host "❌ gcloud CLI não encontrado! Instale o Google Cloud SDK" -ForegroundColor Red
    exit 1 
}

# Verificar autenticação
$account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $account) {
    Write-Host "❌ Não autenticado! Execute: gcloud auth login" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Autenticado: $account" -ForegroundColor Green

# Configurar projeto
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Write-Host "✅ Projeto configurado: $PROJECT_ID" -ForegroundColor Green

# Ler variáveis do .env
$mercadopagoToken = ""
$mercadopagoPublicKey = ""
$secretKey = ""
$dbName = ""
$dbUser = ""
$dbPassword = ""
$cloudSqlConnection = ""

if (Test-Path ".env") {
    $envLines = Get-Content ".env"
    foreach ($line in $envLines) {
        if ($line -match "^MERCADOPAGO_ACCESS_TOKEN=(.+)$") { $mercadopagoToken = $matches[1].Trim() -replace "`r`n|`n|`r", "" }
        if ($line -match "^MERCADOPAGO_PUBLIC_KEY=(.+)$") { $mercadopagoPublicKey = $matches[1].Trim() -replace "`r`n|`n|`r", "" }
        if ($line -match "^SECRET_KEY=(.+)$") { $secretKey = $matches[1].Trim() -replace "`r`n|`n|`r", "" }
        if ($line -match "^DB_NAME=(.+)$") { $dbName = $matches[1].Trim() -replace "`r`n|`n|`r", "" }
        if ($line -match "^DB_USER=(.+)$") { $dbUser = $matches[1].Trim() -replace "`r`n|`n|`r", "" }
        if ($line -match "^DB_PASSWORD=(.+)$") { $dbPassword = $matches[1].Trim() -replace "`r`n|`n|`r", "" }
        if ($line -match "^CLOUD_SQL_CONNECTION_NAME=(.+)$") { $cloudSqlConnection = $matches[1].Trim() -replace "`r`n|`n|`r", "" }
    }
    Write-Host "✅ Variáveis de ambiente carregadas do .env" -ForegroundColor Green
} else {
    Write-Host "⚠️  Arquivo .env não encontrado. Usando configurações padrão." -ForegroundColor Yellow
}

# Build da imagem Docker
Write-Host ""
Write-Host "▶ Construindo imagem Docker..." -ForegroundColor Cyan
$imageTag = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Verificar se Dockerfile.prod existe, caso contrário usar Dockerfile
$dockerfile = if (Test-Path "Dockerfile.prod") { "Dockerfile.prod" } else { "Dockerfile" }
Write-Host "   Usando: $dockerfile" -ForegroundColor Gray

gcloud builds submit --tag $imageTag --file $dockerfile --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build da imagem!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green

# Preparar variáveis de ambiente
$envVarList = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "PYTHONUNBUFFERED=1"
)

if ($mercadopagoToken) { $envVarList += "MERCADOPAGO_ACCESS_TOKEN=$mercadopagoToken" }
if ($mercadopagoPublicKey) { $envVarList += "MERCADOPAGO_PUBLIC_KEY=$mercadopagoPublicKey" }
if ($mercadopagoToken -or $mercadopagoPublicKey) {
    $envVarList += "PAYMENT_GATEWAY_DEFAULT=mercadopago"
    $envVarList += "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/"
    $envVarList += "MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/"
}

if ($secretKey) { $envVarList += "SECRET_KEY=$secretKey" }
if ($dbName) { $envVarList += "DB_NAME=$dbName" }
if ($dbUser) { $envVarList += "DB_USER=$dbUser" }
if ($dbPassword) { $envVarList += "DB_PASSWORD=$dbPassword" }
if ($cloudSqlConnection) { $envVarList += "CLOUD_SQL_CONNECTION_NAME=$cloudSqlConnection" }

$envVarsString = $envVarList -join ","

# Deploy no Cloud Run
Write-Host ""
Write-Host "▶ Fazendo deploy no Cloud Run..." -ForegroundColor Cyan

$deployArgs = @(
    "run", "deploy", $SERVICE_NAME,
    "--image", $imageTag,
    "--platform", "managed",
    "--region", $REGION,
    "--allow-unauthenticated",
    "--set-env-vars", $envVarsString,
    "--memory", "1Gi",
    "--cpu", "2",
    "--timeout", "300",
    "--max-instances", "10",
    "--min-instances", "1",
    "--port", "8080"
)

if ($cloudSqlConnection) {
    $deployArgs += "--add-cloudsql-instances"
    $deployArgs += $cloudSqlConnection
}

& gcloud $deployArgs
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' 2>&1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URL do serviço: $serviceUrl" -ForegroundColor Green
Write-Host ""
Write-Host "✨ Alterações da landing page foram publicadas!" -ForegroundColor Cyan
Write-Host "   - Menu hamburger para mobile implementado" -ForegroundColor White
Write-Host "   - Imagens do slideshow corrigidas" -ForegroundColor White
Write-Host "   - Layout responsivo mobile melhorado" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Aguarde alguns minutos para as mudanças refletirem no site." -ForegroundColor Yellow
Write-Host ""






