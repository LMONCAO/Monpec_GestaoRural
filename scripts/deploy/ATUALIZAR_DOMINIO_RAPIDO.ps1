# 🚀 ATUALIZAR SISTEMA NO DOMÍNIO - GOOGLE CLOUD
# Script simplificado para atualizar o sistema Monpec no domínio monpec.com.br

param(
    [switch]$ApenasBuild = $false,
    [switch]$VerificarStatus = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🚀 ATUALIZAR SISTEMA MONPEC NO DOMÍNIO" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$DOMAIN = "monpec.com.br"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Funções auxiliares
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Error { Write-Host "❌ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Yellow }
function Write-Step { Write-Host "▶️  $args" -ForegroundColor Blue }

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Error "Arquivo manage.py não encontrado!"
    Write-Info "Execute este script na raiz do projeto Django."
    exit 1
}

# Verificar se requirements_producao.txt existe
if (-not (Test-Path "requirements_producao.txt")) {
    Write-Info "Arquivo requirements_producao.txt não encontrado. Criando a partir de requirements.txt..."
    if (Test-Path "requirements.txt") {
        Copy-Item "requirements.txt" "requirements_producao.txt"
        # Adicionar gunicorn e whitenoise se não existirem
        $content = Get-Content "requirements_producao.txt" -Raw
        if ($content -notmatch "gunicorn") {
            Add-Content "requirements_producao.txt" "`ngunicorn>=21.2.0"
        }
        if ($content -notmatch "whitenoise") {
            Add-Content "requirements_producao.txt" "`nwhitenoise>=6.6.0"
        }
        Write-Success "Arquivo requirements_producao.txt criado!"
    } else {
        Write-Error "Arquivo requirements.txt não encontrado!"
        exit 1
    }
}

# Verificar se gcloud está instalado
$gcloudAvailable = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudAvailable) {
    Write-Error "gcloud CLI não encontrado!"
    Write-Info "Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
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
} else {
    Write-Success "Autenticado como: $authCheck"
}

# Configurar projeto
Write-Step "Configurando projeto..."
gcloud config set project $PROJECT_ID | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado: $PROJECT_ID"

# Se apenas verificar status
if ($VerificarStatus) {
    Write-Host ""
    Write-Step "Verificando status do serviço..."
    gcloud run services describe $SERVICE_NAME --region $REGION --format 'table(
        metadata.name,
        status.url,
        status.conditions[0].status,
        status.conditions[0].message
    )'
    
    Write-Host ""
    Write-Step "Verificando domínio..."
    gcloud run domain-mappings describe $DOMAIN --region $REGION --format 'table(
        metadata.name,
        status.conditions[0].status,
        status.conditions[0].message
    )' 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Domínio configurado!"
    } else {
        Write-Info "Domínio não encontrado ou não configurado."
    }
    
    exit 0
}

# Build da imagem
Write-Host ""
Write-Step "Fazendo build da imagem Docker..."
Write-Info "⏳ Isso pode levar 10-15 minutos..."
Write-Host ""

gcloud builds submit --tag $IMAGE_TAG

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build! Verifique os logs acima."
    exit 1
}

Write-Success "Build concluído!"

if ($ApenasBuild) {
    Write-Host ""
    Write-Success "Build concluído! Imagem: $IMAGE_TAG"
    Write-Host ""
    Write-Info "Para fazer deploy, execute:"
    Write-Host "  .\ATUALIZAR_DOMINIO_RAPIDO.ps1" -ForegroundColor Gray
    exit 0
}

# Deploy no Cloud Run
Write-Host ""
Write-Step "Fazendo deploy no Cloud Run..."
Write-Info "⏳ Isso pode levar 2-3 minutos..."
Write-Host ""

gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_TAG `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
    --memory=512Mi `
    --cpu=1 `
    --timeout=300 `
    --max-instances=10

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy! Verifique os logs acima."
    exit 1
}

Write-Success "Deploy concluído!"

# Obter URL do serviço
Write-Host ""
Write-Step "Obtendo informações do serviço..."
$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'

if ($serviceUrl) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ ATUALIZAÇÃO CONCLUÍDA COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 URL do serviço Cloud Run:" -ForegroundColor Cyan
    Write-Host "   $serviceUrl" -ForegroundColor White
    Write-Host ""
    Write-Host "🌐 Domínio configurado:" -ForegroundColor Cyan
    Write-Host "   https://$DOMAIN" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
    Write-Host "   1. Teste o sistema: https://$DOMAIN" -ForegroundColor White
    Write-Host "   2. Verifique os logs se houver problemas:" -ForegroundColor White
    Write-Host "      gcloud run services logs read $SERVICE_NAME --region $REGION" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Error "Não foi possível obter URL do serviço!"
}

Write-Host ""
Write-Info "Para verificar status: .\ATUALIZAR_DOMINIO_RAPIDO.ps1 -VerificarStatus"
Write-Host ""
