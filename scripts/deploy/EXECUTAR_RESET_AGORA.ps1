# 🔥 EXECUTAR RESET E DEPLOY COMPLETO
# Script simplificado para resetar e fazer deploy limpo

$ErrorActionPreference = "Continue"

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$DOMAIN = "monpec.com.br"
$WWW_DOMAIN = "www.monpec.com.br"

function Write-Log { param([string]$Message) Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param([string]$Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param([string]$Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "🔥 RESETAR GOOGLE CLOUD COMPLETAMENTE" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Warning "⚠️  Isso vai EXCLUIR todos os recursos e dados!"
Write-Host ""
Write-Host "Digite 'CONFIRMAR' para continuar:"
$confirm = Read-Host
if ($confirm -ne "CONFIRMAR") {
    Write-Host "Cancelado." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PARTE 1: EXCLUINDO DOMAIN MAPPINGS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Excluindo domain mapping para $DOMAIN..."
gcloud run domain-mappings delete $DOMAIN --region $REGION --quiet 2>&1 | Out-Null
Write-Log "Excluindo domain mapping para $WWW_DOMAIN..."
gcloud run domain-mappings delete $WWW_DOMAIN --region $REGION --quiet 2>&1 | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PARTE 2: EXCLUINDO JOBS CLOUD RUN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$JOB_NAMES = @("migrate-monpec", "collectstatic-monpec", "create-superuser")
foreach ($JOB_NAME in $JOB_NAMES) {
    Write-Log "Excluindo job: $JOB_NAME..."
    gcloud run jobs delete $JOB_NAME --region $REGION --quiet 2>&1 | Out-Null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PARTE 3: EXCLUINDO SERVIÇO CLOUD RUN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Excluindo serviço: $SERVICE_NAME..."
gcloud run services delete $SERVICE_NAME --region $REGION --quiet 2>&1 | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "PARTE 4: EXCLUIR CLOUD SQL?" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Warning "⚠️  Isso exclui TODOS os dados do banco!"
Write-Host ""
Write-Host "Digite 'EXCLUIR' para excluir o banco (ou Enter para manter):"
$confirm_db = Read-Host
if ($confirm_db -eq "EXCLUIR") {
    Write-Log "Excluindo instância Cloud SQL: $INSTANCE_NAME..."
    gcloud sql instances delete $INSTANCE_NAME --quiet 2>&1 | Out-Null
    Write-Success "Banco excluído!"
} else {
    Write-Log "Banco mantido."
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PARTE 5: EXCLUINDO IMAGENS DOCKER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Log "Excluindo imagens..."
try {
    gcloud container images delete $IMAGE_NAME --force-delete-tags --quiet 2>&1 | Out-Null
    Write-Success "Imagens excluídas!"
} catch {
    Write-Log "Imagens não encontradas ou já excluídas."
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Success "✅ RESET CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Deseja fazer o deploy agora? (S/N):"
$deploy = Read-Host
if ($deploy -eq "S" -or $deploy -eq "s") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "INICIANDO DEPLOY..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path "DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1") {
        & ".\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1"
    } else {
        Write-Error "Script de deploy não encontrado!"
    }
} else {
    Write-Host ""
    Write-Host "Para fazer deploy depois, execute:" -ForegroundColor Yellow
    Write-Host "   .\DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1"
    Write-Host ""
}






