# ☁️ SCRIPT DE DEPLOY PARA GOOGLE CLOUD PLATFORM
# PowerShell script para fazer deploy no GCP

param(
    [string]$Projeto = "monpec-sistema-rural",
    [string]$Regiao = "us-central1",
    [string]$Servico = "monpec",
    [switch]$ApenasBuild = $false
)

$ErrorActionPreference = "Stop"

Write-Host "☁️ DEPLOY MONPEC PARA GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Cores
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Yellow }
function Write-Step { Write-Host "▶ $args" -ForegroundColor Blue }

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Error "❌ Arquivo manage.py não encontrado!"
    Write-Error "Execute este script na raiz do projeto Django."
    exit 1
}

# Verificar se gcloud está instalado
$gcloudAvailable = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudAvailable) {
    Write-Error "❌ gcloud CLI não encontrado!"
    Write-Info "Instale o Google Cloud SDK:"
    Write-Host "  https://cloud.google.com/sdk/docs/install" -ForegroundColor Gray
    Write-Host "  Ou: choco install gcloudsdk" -ForegroundColor Gray
    exit 1
}

Write-Step "Configurações do Deploy:"
Write-Host "  Projeto: $Projeto" -ForegroundColor Gray
Write-Host "  Região: $Regiao" -ForegroundColor Gray
Write-Host "  Serviço: $Servico" -ForegroundColor Gray
Write-Host ""

# Verificar se está autenticado
Write-Step "Verificando autenticação..."
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Info "⚠ Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Falha na autenticação!"
        exit 1
    }
}
Write-Success "✅ Autenticado!"

# Configurar projeto
Write-Step "Configurando projeto..."
gcloud config set project $Projeto
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro ao configurar projeto!"
    exit 1
}
Write-Success "✅ Projeto configurado!"

# Habilitar APIs necessárias
Write-Step "Habilitando APIs..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudresourcemanager.googleapis.com"
)

foreach ($api in $apis) {
    Write-Info "  Habilitando $api..."
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Success "✅ APIs habilitadas!"

# Verificar se Dockerfile existe
if (-not (Test-Path "Dockerfile")) {
    Write-Error "❌ Dockerfile não encontrado!"
    Write-Info "Criando Dockerfile básico..."
    # Aqui poderia criar o Dockerfile automaticamente
    exit 1
}

# Build da imagem
Write-Step "Fazendo build da imagem Docker..."
$imageTag = "gcr.io/$Projeto/$Servico"
gcloud builds submit --tag $imageTag
if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro no build!"
    exit 1
}
Write-Success "✅ Build concluído!"

if ($ApenasBuild) {
    Write-Host ""
    Write-Success "🎉 Build concluído! Imagem: $imageTag"
    Write-Host ""
    Write-Info "Para fazer deploy, execute:"
    Write-Host "  gcloud run deploy $Servico --image $imageTag --region $Regiao" -ForegroundColor Gray
    exit 0
}

# Deploy no Cloud Run
Write-Step "Fazendo deploy no Cloud Run..."
gcloud run deploy $Servico `
    --image $imageTag `
    --platform managed `
    --region $Regiao `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"

if ($LASTEXITCODE -ne 0) {
    Write-Error "❌ Erro no deploy!"
    exit 1
}

# Obter URL do serviço
Write-Step "Obtendo URL do serviço..."
$serviceUrl = gcloud run services describe $Servico --region $Regiao --format 'value(status.url)'
if ($serviceUrl) {
    Write-Success "✅ Deploy concluído!"
    Write-Host ""
    Write-Host "🌐 URL do serviço:" -ForegroundColor Cyan
    Write-Host "   $serviceUrl" -ForegroundColor Green
    Write-Host ""
    Write-Info "📊 Comandos úteis:"
    Write-Host "   Ver logs: gcloud run services logs read $Servico --region $Regiao" -ForegroundColor Gray
    Write-Host "   Ver status: gcloud run services describe $Servico --region $Regiao" -ForegroundColor Gray
    Write-Host "   Abrir no navegador: start $serviceUrl" -ForegroundColor Gray
} else {
    Write-Error "❌ Não foi possível obter URL do serviço!"
}

Write-Host ""
Write-Success "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
Write-Host ""






