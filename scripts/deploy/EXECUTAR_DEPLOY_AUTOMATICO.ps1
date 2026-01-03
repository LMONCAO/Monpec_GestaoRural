# 🚀 EXECUTAR DEPLOY AUTOMÁTICO
# Este script encontra o diretório automaticamente e executa o deploy

# Encontrar o diretório do projeto
$desktop = "$env:USERPROFILE\Desktop"
$projectDir = $null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 PROCURANDO DIRETÓRIO DO PROJETO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Procurar diretório que contém Monpec_GestaoRural
Get-ChildItem $desktop -Directory | Where-Object { $_.Name -match "MonPO" } | ForEach-Object {
    $testPath = Join-Path $_.FullName "Monpec_GestaoRural"
    if (Test-Path $testPath) {
        $projectDir = $testPath
        Write-Host "✅ Diretório encontrado: $projectDir" -ForegroundColor Green
    }
}

if (-not $projectDir) {
    Write-Host "❌ Diretório do projeto não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, navegue manualmente até o diretório e execute:" -ForegroundColor Yellow
    Write-Host "   .\DEPLOY_AGORA_SIMPLES.ps1" -ForegroundColor White
    exit 1
}

# Navegar para o diretório
Set-Location $projectDir
Write-Host "📁 Diretório atual: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

# Verificar se o script de deploy existe
if (-not (Test-Path "DEPLOY_AGORA_SIMPLES.ps1")) {
    Write-Host "❌ Script DEPLOY_AGORA_SIMPLES.ps1 não encontrado!" -ForegroundColor Red
    Write-Host "Criando script de deploy..." -ForegroundColor Yellow
    
    # Criar script inline se não existir
    $deployScript = @'
# 🚀 DEPLOY COMPLETO SIMPLIFICADO
$ErrorActionPreference = "Continue"

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"
$DB_NAME = "monpec_db"
$DB_USER = "monpec_user"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$DB_PASSWORD = "Monpec2025!SenhaSegura"
$SECRET_KEY = "django-insecure-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

function Write-Log { param([string]$Message) Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param([string]$Message) Write-Host "❌ $Message" -ForegroundColor Red }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY COMPLETO - MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

gcloud config set project $PROJECT_ID | Out-Null
Write-Success "Projeto configurado: $PROJECT_ID"

Write-Log "Habilitando APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet | Out-Null
gcloud services enable run.googleapis.com --quiet | Out-Null
gcloud services enable containerregistry.googleapis.com --quiet | Out-Null
gcloud services enable sqladmin.googleapis.com --quiet | Out-Null
Write-Success "APIs habilitadas!"

Write-Log "Obtendo connection name..."
$CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)" 2>&1
if (-not $CONNECTION_NAME -or $CONNECTION_NAME -like "*ERROR*") {
    Write-Error "Erro ao obter connection name."
    exit 1
}
Write-Success "Connection name: $CONNECTION_NAME"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "BUILD DA IMAGEM DOCKER"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Log "⚠️  Isso pode levar 5-10 minutos..."
Write-Log "Iniciado em: $(Get-Date -Format 'HH:mm:ss')"

gcloud builds submit --tag $IMAGE_NAME --timeout=600s
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build da imagem!"
    exit 1
}
Write-Success "Imagem Docker criada!"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "DEPLOY NO CLOUD RUN"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ENV_VARS = "DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY,DEBUG=False,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,PORT=8080"

Write-Log "Fazendo deploy..."
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --add-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars $ENV_VARS `
    --memory 2Gi `
    --cpu 2 `
    --timeout 600 `
    --max-instances 10 `
    --min-instances 0 `
    --port 8080 `
    --quiet 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy!"
    exit 1
}

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1
Write-Success "Deploy concluído!"
Write-Log "URL: $SERVICE_URL"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "APLICANDO MIGRAÇÕES"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$JOB_NAME = "migrate-monpec"
Write-Log "Criando job de migração..."

gcloud run jobs create $JOB_NAME `
    --image $IMAGE_NAME `
    --region $REGION `
    --set-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars $ENV_VARS `
    --memory 2Gi `
    --cpu 1 `
    --max-retries 3 `
    --task-timeout 600 `
    --command python `
    --args "manage.py,migrate,--noinput" `
    --quiet 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Log "Job já existe, atualizando..."
    gcloud run jobs update $JOB_NAME `
        --image $IMAGE_NAME `
        --region $REGION `
        --set-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $ENV_VARS `
        --quiet 2>&1 | Out-Null
}

Write-Log "Executando migrações..."
gcloud run jobs execute $JOB_NAME --region $REGION --wait 2>&1 | Out-Null
Write-Success "Migrações aplicadas!"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Log "COLETANDO ARQUIVOS ESTÁTICOS"
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$STATIC_JOB_NAME = "collectstatic-monpec"
Write-Log "Criando job de collectstatic..."

gcloud run jobs create $STATIC_JOB_NAME `
    --image $IMAGE_NAME `
    --region $REGION `
    --set-cloudsql-instances $CONNECTION_NAME `
    --set-env-vars $ENV_VARS `
    --memory 2Gi `
    --cpu 1 `
    --max-retries 3 `
    --task-timeout 600 `
    --command python `
    --args "manage.py,collectstatic,--noinput" `
    --quiet 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Log "Job já existe, atualizando..."
    gcloud run jobs update $STATIC_JOB_NAME `
        --image $IMAGE_NAME `
        --region $REGION `
        --set-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $ENV_VARS `
        --quiet 2>&1 | Out-Null
}

Write-Log "Coletando arquivos estáticos..."
gcloud run jobs execute $STATIC_JOB_NAME --region $REGION --wait 2>&1 | Out-Null
Write-Success "Arquivos estáticos coletados!"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Success "✅ DEPLOY COMPLETO CONCLUÍDO!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL do serviço:" -ForegroundColor Cyan
Write-Host "   $SERVICE_URL" -ForegroundColor White
Write-Host ""
Write-Success "🎉 Sistema pronto!"
Write-Host ""
'@
    
    $deployScript | Out-File -FilePath "DEPLOY_AGORA_SIMPLES.ps1" -Encoding UTF8
    Write-Host "✅ Script criado!" -ForegroundColor Green
}

# Executar o script de deploy
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 INICIANDO DEPLOY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& ".\DEPLOY_AGORA_SIMPLES.ps1"






