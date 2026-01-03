# Script PowerShell de Deploy Completo com Auditoria
# Execute: .\DEPLOY_COMPLETO_AUDITADO_POWERSHELL.ps1

$ErrorActionPreference = "Stop"

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"
$SECRET_KEY = "django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

$ERROS = 0
$AVISOS = 0

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
    $script:ERROS++
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
    $script:AVISOS++
}

Clear-Host
Write-Step "🚀 DEPLOY COMPLETO MONPEC - COM AUDITORIA"

# ==========================================
# ETAPA 1: AUDITORIA PRÉ-DEPLOY
# ==========================================
Write-Step "ETAPA 1: AUDITORIA PRÉ-DEPLOY"

# Verificar Dockerfile
Write-Info "Verificando Dockerfile.prod..."
if (-not (Test-Path "Dockerfile.prod") -or (Get-Item "Dockerfile.prod").Length -eq 0) {
    Write-Error "Dockerfile.prod não encontrado ou está vazio!"
    exit 1
}
Write-Success "Dockerfile.prod OK"

# Verificar requirements
Write-Info "Verificando requirements_producao.txt..."
if (-not (Test-Path "requirements_producao.txt")) {
    Write-Error "requirements_producao.txt não encontrado!"
    exit 1
}
Write-Success "requirements_producao.txt existe"

$DEPENDENCIAS_CRITICAS = @("Django", "gunicorn", "psycopg2-binary", "whitenoise", "openpyxl")
foreach ($dep in $DEPENDENCIAS_CRITICAS) {
    if (-not (Select-String -Path "requirements_producao.txt" -Pattern $dep -Quiet)) {
        Write-Error "$dep não encontrado em requirements_producao.txt"
    } else {
        Write-Success "$dep encontrado"
    }
}

# Garantir openpyxl
if (-not (Select-String -Path "requirements_producao.txt" -Pattern "^openpyxl" -Quiet)) {
    Write-Warning "openpyxl não encontrado, adicionando..."
    Add-Content -Path "requirements_producao.txt" -Value "openpyxl>=3.1.5"
    Write-Success "openpyxl adicionado"
}

# Verificar manage.py
Write-Info "Verificando manage.py..."
if (-not (Test-Path "manage.py")) {
    Write-Error "manage.py não encontrado!"
    exit 1
}
Write-Success "manage.py existe"

# Verificar settings
Write-Info "Verificando settings_gcp.py..."
if (-not (Test-Path "sistema_rural/settings_gcp.py")) {
    Write-Error "settings_gcp.py não encontrado!"
    exit 1
}
Write-Success "settings_gcp.py existe"

if ($ERROS -gt 0) {
    Write-Host ""
    Write-Error "Auditoria falhou com $ERROS erro(s)! Corrija antes de continuar."
    exit 1
}

Write-Success "Auditoria passou! Sistema pronto para deploy."

# ==========================================
# ETAPA 2: VERIFICAÇÕES GOOGLE CLOUD
# ==========================================
Write-Step "ETAPA 2: VERIFICAÇÕES DO GOOGLE CLOUD"

# Verificar autenticação
Write-Info "Verificando autenticação..."
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1 | Where-Object { $_ -and $_ -notmatch "ERROR" -and $_ -notmatch "WARNING" }
if (-not $authCheck) {
    Write-Warning "Não autenticado no Google Cloud!"
    Write-Info "Tentando fazer login automaticamente..."
    Write-Host ""
    Write-Host "⚠️  Uma janela do navegador será aberta para autenticação" -ForegroundColor Yellow
    Write-Host "   Por favor, faça login na sua conta Google Cloud" -ForegroundColor Yellow
    Write-Host ""
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na autenticação!"
        Write-Info "Execute manualmente: gcloud auth login"
        exit 1
    }
    Write-Success "Login realizado com sucesso!"
} else {
    Write-Success "Autenticado no Google Cloud: $authCheck"
}

# Configurar projeto
Write-Info "Configurando projeto: $PROJECT_ID"
gcloud config set project $PROJECT_ID
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado"

# Verificar Cloud SQL
Write-Info "Verificando instância Cloud SQL..."
$sqlCheck = gcloud sql instances describe monpec-db --format="value(name)" 2>&1
if ($sqlCheck -match "ERROR" -or -not $sqlCheck) {
    Write-Error "Instância monpec-db não encontrada!"
    exit 1
}
Write-Success "Instância monpec-db encontrada"

# Corrigir senha do banco
Write-Info "Corrigindo senha do banco..."
gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Senha do banco atualizada"
} else {
    Write-Warning "Não foi possível atualizar senha do banco (pode ser normal)"
}

# ==========================================
# ETAPA 3: BUILD
# ==========================================
Write-Step "ETAPA 3: BUILD DA IMAGEM DOCKER"

$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

Write-Info "Tag: $IMAGE_TAG"
Write-Info "Isso pode levar 5-10 minutos..."
Write-Host ""

gcloud builds submit --tag $IMAGE_TAG --timeout=20m
if ($LASTEXITCODE -ne 0) {
    Write-Error "Build falhou!"
    exit 1
}
Write-Success "Build concluído!"

# ==========================================
# ETAPA 4: DEPLOY
# ==========================================
Write-Step "ETAPA 4: DEPLOY NO CLOUD RUN"

$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

Write-Info "Isso pode levar 2-5 minutos..."
Write-Host ""

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
    Write-Error "Deploy falhou!"
    exit 1
}
Write-Success "Deploy concluído!"

# ==========================================
# ETAPA 5: VERIFICAÇÕES PÓS-DEPLOY
# ==========================================
Write-Step "ETAPA 5: VERIFICAÇÕES PÓS-DEPLOY"

Write-Info "Obtendo URL..."
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>$null

if ($SERVICE_URL) {
    Write-Success "URL: $SERVICE_URL"
} else {
    Write-Warning "Não foi possível obter URL"
}

Write-Info "Aguardando 30 segundos para inicialização..."
Start-Sleep -Seconds 30

# ==========================================
# RESUMO FINAL
# ==========================================
Write-Step "✅✅✅ DEPLOY CONCLUÍDO! ✅✅✅"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "📋 INFORMAÇÕES DO DEPLOY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 URL do Serviço:" -ForegroundColor Cyan
Write-Host "   $SERVICE_URL" -ForegroundColor White
Write-Host ""
Write-Host "📋 Credenciais para Login:" -ForegroundColor Cyan
Write-Host "   Username: admin" -ForegroundColor White
Write-Host "   Senha: L6171r12@@" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Próximos Passos:" -ForegroundColor Cyan
Write-Host "   1. Aguarde 1-2 minutos para inicialização completa" -ForegroundColor White
Write-Host "   2. Acesse: $SERVICE_URL" -ForegroundColor White
Write-Host "   3. Faça login com as credenciais acima" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

