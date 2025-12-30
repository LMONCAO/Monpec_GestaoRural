# 🚀 DEPLOY RÁPIDO COM MERCADO PAGO
# Script simplificado para deploy rápido

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🚀 DEPLOY RÁPIDO - MONPEC COM MERCADO PAGO" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$Projeto = "monpec-sistema-rural"
$Regiao = "us-central1"
$Servico = "monpec"

# Verificar .env
if (-not (Test-Path ".env")) {
    Write-Host "❌ Arquivo .env não encontrado!" -ForegroundColor Red
    Write-Host "Crie o arquivo .env com as credenciais do Mercado Pago" -ForegroundColor Yellow
    exit 1
}

# Ler credenciais
$envContent = Get-Content ".env" -Raw
$token = ""
$publicKey = ""

if ($envContent -match "MERCADOPAGO_ACCESS_TOKEN=(.+)") {
    $token = $matches[1].Trim() -replace "`r`n|`n|`r", ""
}
if ($envContent -match "MERCADOPAGO_PUBLIC_KEY=(.+)") {
    $publicKey = $matches[1].Trim() -replace "`r`n|`n|`r", ""
}

if (-not $token) {
    Write-Host "❌ MERCADOPAGO_ACCESS_TOKEN não encontrado no .env!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Credenciais do Mercado Pago encontradas" -ForegroundColor Green
Write-Host ""

# Configurar projeto
Write-Host "▶ Configurando projeto..." -ForegroundColor Blue
gcloud config set project $Projeto 2>&1 | Out-Null

# Build e Deploy
Write-Host "▶ Fazendo build da imagem..." -ForegroundColor Blue
$imageTag = "gcr.io/$Projeto/$Servico"
gcloud builds submit --tag $imageTag --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build concluído!" -ForegroundColor Green
Write-Host ""

# Preparar variáveis de ambiente
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "MERCADOPAGO_ACCESS_TOKEN=$token",
    "MERCADOPAGO_PUBLIC_KEY=$publicKey",
    "PAYMENT_GATEWAY_DEFAULT=mercadopago",
    "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/",
    "MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/"
)

# Adicionar outras variáveis do .env se existirem
$envLines = Get-Content ".env"
foreach ($line in $envLines) {
    if ($line -match "^SECRET_KEY=(.+)$") {
        $envVars += "SECRET_KEY=$($matches[1].Trim())"
    }
    if ($line -match "^DB_NAME=(.+)$") {
        $envVars += "DB_NAME=$($matches[1].Trim())"
    }
    if ($line -match "^DB_USER=(.+)$") {
        $envVars += "DB_USER=$($matches[1].Trim())"
    }
    if ($line -match "^DB_PASSWORD=(.+)$") {
        $envVars += "DB_PASSWORD=$($matches[1].Trim())"
    }
    if ($line -match "^CLOUD_SQL_CONNECTION_NAME=(.+)$") {
        $envVars += "CLOUD_SQL_CONNECTION_NAME=$($matches[1].Trim())"
    }
}

$envVarsString = $envVars -join ","

Write-Host "▶ Fazendo deploy no Cloud Run..." -ForegroundColor Blue
gcloud run deploy $Servico `
    --image $imageTag `
    --platform managed `
    --region $Regiao `
    --allow-unauthenticated `
    --set-env-vars $envVarsString `
    --memory=1Gi `
    --cpu=2 `
    --timeout=300 `
    --max-instances=10 `
    --min-instances=1 `
    --port=8080

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

# Obter URL
$serviceUrl = gcloud run services describe $Servico --region $Regiao --format 'value(status.url)' 2>&1

Write-Host ""
Write-Host "✅ DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL do serviço:" -ForegroundColor Cyan
Write-Host "   $serviceUrl" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Mercado Pago configurado:" -ForegroundColor Cyan
Write-Host "   ✅ Access Token: Configurado" -ForegroundColor Green
Write-Host "   ✅ Public Key: Configurado" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Teste agora:" -ForegroundColor Yellow
Write-Host "   $serviceUrl/assinaturas/" -ForegroundColor Gray
Write-Host ""

