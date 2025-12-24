# Script de Deploy Automático - MONPEC para Google Cloud Run (PowerShell)
# Uso: .\deploy.ps1 [PROJECT_ID] [REGION]

param(
    [string]$ProjectId = "SEU_PROJECT_ID",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

$ServiceName = "monpec"
$ImageName = "gcr.io/$ProjectId/$ServiceName"

Write-Host "🚀 Iniciando deploy do MONPEC para Google Cloud Run" -ForegroundColor Green
Write-Host "Projeto: $ProjectId" -ForegroundColor Yellow
Write-Host "Região: $Region" -ForegroundColor Yellow
Write-Host ""

# Verificar se gcloud está instalado
try {
    $null = gcloud --version 2>&1
} catch {
    Write-Host "❌ Google Cloud SDK não está instalado" -ForegroundColor Red
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verificar login
Write-Host "Verificando autenticação..." -ForegroundColor Yellow
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)"
if (-not $activeAccount) {
    Write-Host "Faça login no Google Cloud:" -ForegroundColor Yellow
    gcloud auth login
}

# Definir projeto
Write-Host "Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# Habilitar APIs necessárias
Write-Host "Habilitando APIs necessárias..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable sqladmin.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

# Build da imagem
Write-Host "🔨 Construindo imagem Docker..." -ForegroundColor Yellow
gcloud builds submit --tag $ImageName --quiet

# Deploy no Cloud Run
Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --port 8080 `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
    --quiet

# Obter URL do serviço
$ServiceUrl = gcloud run services describe $ServiceName --region $Region --format="value(status.url)"

Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host "URL do serviço: $ServiceUrl" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Lembre-se de:" -ForegroundColor Yellow
Write-Host "1. Configurar variáveis de ambiente (SECRET_KEY, DB_*, etc.)"
Write-Host "2. Conectar ao Cloud SQL se usar banco de dados"
Write-Host "3. Executar migrações: gcloud run jobs execute monpec-migrate --region $Region"
Write-Host "4. Configurar domínio personalizado se necessário"




















