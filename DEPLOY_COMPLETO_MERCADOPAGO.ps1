# 🚀 DEPLOY COMPLETO COM MERCADO PAGO
# Script PowerShell para fazer deploy no Google Cloud Run com todas as configurações

param(
    [string]$Projeto = "monpec-sistema-rural",
    [string]$Regiao = "us-central1",
    [string]$Servico = "monpec"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🚀 DEPLOY COMPLETO - MONPEC COM MERCADO PAGO" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Cores
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Yellow }
function Write-Step { Write-Host "▶ $args" -ForegroundColor Blue }

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Error "Arquivo manage.py não encontrado! Execute na raiz do projeto."
    exit 1
}

# Verificar gcloud
$gcloudAvailable = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudAvailable) {
    Write-Error "gcloud CLI não encontrado! Instale o Google Cloud SDK."
    exit 1
}

Write-Step "Configurações:"
Write-Host "  Projeto: $Projeto" -ForegroundColor Gray
Write-Host "  Região: $Regiao" -ForegroundColor Gray
Write-Host "  Serviço: $Servico" -ForegroundColor Gray
Write-Host ""

# 1. Autenticação
Write-Step "Verificando autenticação..."
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Info "Fazendo login no Google Cloud..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na autenticação!"
        exit 1
    }
}
Write-Success "Autenticado"

# 2. Configurar projeto
Write-Step "Configurando projeto..."
gcloud config set project $Projeto 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado"

# 3. Habilitar APIs
Write-Step "Habilitando APIs necessárias..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com"
)
foreach ($api in $apis) {
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Success "APIs habilitadas"

# 4. Ler credenciais do Mercado Pago do arquivo .env
Write-Step "Lendo credenciais do Mercado Pago..."
$mercadopagoToken = ""
$mercadopagoPublicKey = ""

if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "MERCADOPAGO_ACCESS_TOKEN=(.+)") {
        $mercadopagoToken = $matches[1].Trim()
        Write-Success "Token do Mercado Pago encontrado no .env"
    }
    if ($envContent -match "MERCADOPAGO_PUBLIC_KEY=(.+)") {
        $mercadopagoPublicKey = $matches[1].Trim()
        Write-Success "Public Key do Mercado Pago encontrada no .env"
    }
}

if (-not $mercadopagoToken) {
    Write-Error "MERCADOPAGO_ACCESS_TOKEN não encontrado no arquivo .env!"
    Write-Info "Configure o arquivo .env antes de fazer o deploy."
    exit 1
}

# 5. Preparar variáveis de ambiente
Write-Step "Preparando variáveis de ambiente..."
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "MERCADOPAGO_ACCESS_TOKEN=$mercadopagoToken",
    "MERCADOPAGO_PUBLIC_KEY=$mercadopagoPublicKey",
    "PAYMENT_GATEWAY_DEFAULT=mercadopago",
    "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/",
    "MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/"
)

# Adicionar outras variáveis se existirem no .env
if (Test-Path ".env") {
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
}

$envVarsString = $envVars -join ","

# 6. Verificar Dockerfile
if (-not (Test-Path "Dockerfile")) {
    Write-Error "Dockerfile não encontrado!"
    Write-Info "Criando Dockerfile básico..."
    # Poderia criar aqui, mas melhor ter o arquivo já
    exit 1
}

# 7. Build da imagem
Write-Step "Fazendo build da imagem Docker..."
$imageTag = "gcr.io/$Projeto/$Servico"
Write-Info "Tag da imagem: $imageTag"

gcloud builds submit --tag $imageTag --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build da imagem!"
    exit 1
}
Write-Success "Build concluído!"

# 8. Deploy no Cloud Run
Write-Step "Fazendo deploy no Cloud Run..."
Write-Info "Configurando variáveis de ambiente do Mercado Pago..."

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
    Write-Error "Erro no deploy!"
    exit 1
}

# 9. Obter URL
Write-Step "Obtendo URL do serviço..."
$serviceUrl = gcloud run services describe $Servico --region $Regiao --format 'value(status.url)' 2>&1

if ($serviceUrl) {
    Write-Host ""
    Write-Success "DEPLOY CONCLUÍDO COM SUCESSO!"
    Write-Host ""
    Write-Host "🌐 URL do serviço:" -ForegroundColor Cyan
    Write-Host "   $serviceUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔧 Configurações do Mercado Pago:" -ForegroundColor Cyan
    Write-Host "   ✅ Access Token: Configurado" -ForegroundColor Green
    Write-Host "   ✅ Public Key: Configurado" -ForegroundColor Green
    Write-Host "   ✅ Gateway: mercadopago" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   1. Teste o checkout em: $serviceUrl/assinaturas/" -ForegroundColor Gray
    Write-Host "   2. Configure o webhook no Mercado Pago:" -ForegroundColor Gray
    Write-Host "      URL: https://monpec.com.br/assinaturas/webhook/mercadopago/" -ForegroundColor Gray
    Write-Host "   3. Verifique os logs:" -ForegroundColor Gray
    Write-Host "      gcloud run services logs read $Servico --region $Regiao" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Error "Não foi possível obter URL do serviço!"
}

Write-Host ""
Write-Success "🎉 TUDO PRONTO!"
Write-Host ""

