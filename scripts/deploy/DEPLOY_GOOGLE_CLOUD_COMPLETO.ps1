# Script completo de deploy para Google Cloud Run - Sistema MONPEC (PowerShell)
# Execute este script para fazer o deploy completo no Google Cloud

$ErrorActionPreference = "Stop"

# Cores
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Info { Write-Host "→ $args" -ForegroundColor Yellow }
function Write-Step { Write-Host "▶ $args" -ForegroundColor Cyan }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY GOOGLE CLOUD - SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configurações padrão
$ProjectId = if ($env:GCP_PROJECT) { $env:GCP_PROJECT } else { 
    $proj = gcloud config get-value project 2>&1
    if ($LASTEXITCODE -eq 0) { $proj.Trim() } else { $null }
}

$ServiceName = if ($env:CLOUD_RUN_SERVICE) { $env:CLOUD_RUN_SERVICE } else { "monpec" }
$Region = if ($env:CLOUD_RUN_REGION) { $env:CLOUD_RUN_REGION } else { "us-central1" }
$ImageName = "gcr.io/$ProjectId/$ServiceName"

# Verificar gcloud
Write-Step "Verificando gcloud CLI..."
try {
    $null = gcloud --version 2>&1
    Write-Success "gcloud CLI encontrado"
} catch {
    Write-Error "gcloud CLI não está instalado!"
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verificar autenticação
Write-Step "Verificando autenticação..."
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Info "Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na autenticação!"
        exit 1
    }
}
Write-Success "Autenticado"

# Configurar projeto
if (-not $ProjectId) {
    Write-Error "PROJECT_ID não definido!"
    Write-Host "Defina com: `$env:GCP_PROJECT='seu-projeto-id'" -ForegroundColor Yellow
    Write-Host "Ou configure com: gcloud config set project SEU-PROJETO-ID" -ForegroundColor Yellow
    exit 1
}

Write-Step "Configurando projeto: $ProjectId"
gcloud config set project $ProjectId
Write-Success "Projeto configurado"

# Habilitar APIs
Write-Step "Habilitando APIs necessárias..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    Write-Info "  Habilitando $api..."
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Success "APIs habilitadas"

# Verificar Dockerfile
Write-Step "Verificando Dockerfile..."
$dockerfile = if (Test-Path "Dockerfile.prod") { "Dockerfile.prod" } else { "Dockerfile" }
if (-not (Test-Path $dockerfile)) {
    Write-Error "Dockerfile não encontrado!"
    exit 1
}
Write-Success "Dockerfile encontrado: $dockerfile"

# Verificar requirements.txt
if (-not (Test-Path "requirements.txt")) {
    Write-Error "requirements.txt não encontrado!"
    exit 1
}

# Build da imagem
Write-Step "Fazendo build da imagem Docker..."
Write-Info "  Imagem: $ImageName`:latest"
gcloud builds submit --tag "$ImageName`:latest" --timeout=20m
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build da imagem!"
    exit 1
}
Write-Success "Build concluído"

# Configurar variáveis de ambiente
Write-Step "Configurando variáveis de ambiente..."
$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

if ($env:SECRET_KEY) {
    $envVars += ",SECRET_KEY=$($env:SECRET_KEY)"
    Write-Info "  SECRET_KEY: definida"
} else {
    Write-Info "  SECRET_KEY: não definida (será necessário configurar depois)"
}

if ($env:DB_NAME) { $envVars += ",DB_NAME=$($env:DB_NAME)" }
if ($env:DB_USER) { $envVars += ",DB_USER=$($env:DB_USER)" }
if ($env:DB_PASSWORD) { $envVars += ",DB_PASSWORD=$($env:DB_PASSWORD)" }
if ($env:DB_HOST) { $envVars += ",DB_HOST=$($env:DB_HOST)" }
if ($env:CLOUD_SQL_CONNECTION_NAME) { 
    $envVars += ",CLOUD_SQL_CONNECTION_NAME=$($env:CLOUD_SQL_CONNECTION_NAME)" 
}

# Deploy no Cloud Run
Write-Step "Fazendo deploy no Cloud Run..."
Write-Info "  Serviço: $ServiceName"
Write-Info "  Região: $Region"
Write-Info "  Imagem: $ImageName`:latest"

$deployArgs = @(
    "run", "deploy", $ServiceName,
    "--image", "$ImageName`:latest",
    "--platform", "managed",
    "--region", $Region,
    "--allow-unauthenticated",
    "--set-env-vars", $envVars,
    "--memory=1Gi",
    "--cpu=2",
    "--timeout=300",
    "--max-instances=10",
    "--min-instances=1"
)

if ($env:CLOUD_SQL_CONNECTION_NAME) {
    $deployArgs += "--add-cloudsql-instances=$($env:CLOUD_SQL_CONNECTION_NAME)"
    Write-Info "  Cloud SQL: $($env:CLOUD_SQL_CONNECTION_NAME)"
}

& gcloud $deployArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy!"
    exit 1
}

Write-Success "Deploy concluído!"

# Obter URL
Write-Step "Obtendo URL do serviço..."
$serviceUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)"
Write-Success "Serviço disponível em: $serviceUrl"

# Aplicar migrações
Write-Step "Aplicando migrações do banco de dados..."
Write-Info "Isso pode levar alguns minutos..."

# Criar job de migração (se não existir)
gcloud run jobs create migrate-monpec `
    --image "$ImageName`:latest" `
    --region $Region `
    --set-env-vars $envVars `
    --command python `
    --args "manage.py,migrate,--noinput" `
    --max-retries 3 `
    --task-timeout 600 `
    2>&1 | Out-Null

# Executar job
gcloud run jobs execute migrate-monpec --region $Region --wait 2>&1 | Out-Null

Write-Success "Migrações aplicadas"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Success "DEPLOY CONCLUÍDO COM SUCESSO!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Informações:" -ForegroundColor Cyan
Write-Host "  • Serviço: $ServiceName"
Write-Host "  • URL: $serviceUrl"
Write-Host "  • Região: $Region"
Write-Host "  • Projeto: $ProjectId"
Write-Host ""
Write-Host "🔗 Próximos passos:" -ForegroundColor Yellow
Write-Host "  1. Configure o domínio monpec.com.br para apontar para: $serviceUrl"
Write-Host "  2. Configure variáveis de ambiente adicionais se necessário"
Write-Host "  3. Verifique os logs: gcloud run services logs read $ServiceName --region $Region"
Write-Host "  4. Teste o acesso em: $serviceUrl"
Write-Host ""
