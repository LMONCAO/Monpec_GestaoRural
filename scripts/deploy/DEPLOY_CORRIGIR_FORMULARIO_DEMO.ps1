# 🚀 DEPLOY PARA CORRIGIR FORMULÁRIO DE DEMONSTRAÇÃO
# Corrige o erro CSRF no formulário de demonstração

$ErrorActionPreference = "Stop"

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY - CORREÇÃO FORMULÁRIO DEMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Funções auxiliares
function Write-Step {
    param([string]$Message)
    Write-Host "▶ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# 1. Verificar gcloud
Write-Step "Verificando gcloud CLI..."
try {
    $null = gcloud --version 2>&1 | Out-Null
    Write-Success "gcloud encontrado"
} catch {
    Write-Error "gcloud CLI não está instalado!"
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# 2. Verificar autenticação
Write-Step "Verificando autenticação..."
$account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $account -or $account -match "ERROR") {
    Write-Error "Você não está autenticado no Google Cloud!"
    Write-Host "Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}
Write-Success "Autenticado como: $account"

# 3. Configurar projeto
Write-Step "Configurando projeto..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado: $PROJECT_ID"

# 4. Build da imagem
Write-Step "Fazendo build da imagem Docker..."
Write-Host "   Isso pode levar alguns minutos..." -ForegroundColor Gray
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"
$LATEST_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:latest"

gcloud builds submit --tag $IMAGE_TAG 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build!"
    exit 1
}
Write-Success "Build concluído"

# 5. Marcar como latest
Write-Step "Marcando imagem como latest..."
gcloud container images add-tag $IMAGE_TAG $LATEST_TAG --quiet 2>&1 | Out-Null
Write-Success "Imagem marcada como latest"

# 6. Deploy no Cloud Run
Write-Step "Fazendo deploy no Cloud Run..."
Write-Host "   Atualizando com correções CSRF..." -ForegroundColor Gray

$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db",
    "DB_NAME=monpec_db",
    "DB_USER=monpec_user",
    "DB_PASSWORD=L6171r12@@jjms"
)

$envVarsString = $envVars -join ","

gcloud run deploy $SERVICE_NAME `
    --image $LATEST_TAG `
    --region=$REGION `
    --platform managed `
    --allow-unauthenticated `
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db `
    --set-env-vars $envVarsString `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy!"
    exit 1
}
Write-Success "Deploy concluído!"

# 7. Obter URL do serviço
Write-Step "Obtendo URL do serviço..."
$serviceUrl = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Success "DEPLOY CONCLUÍDO COM SUCESSO!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL do serviço:" -ForegroundColor Cyan
Write-Host "   $serviceUrl" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Correções aplicadas:" -ForegroundColor Yellow
Write-Host "   • Domínio adicionado ao CSRF_TRUSTED_ORIGINS" -ForegroundColor White
Write-Host "   • Tratamento de erros melhorado" -ForegroundColor White
Write-Host ""
Write-Host "📋 Próximo passo:" -ForegroundColor Yellow
Write-Host "   Teste o formulário de demonstração em:" -ForegroundColor White
Write-Host "   $serviceUrl" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Aguarde 30-60 segundos para o serviço inicializar completamente" -ForegroundColor Yellow
Write-Host ""



