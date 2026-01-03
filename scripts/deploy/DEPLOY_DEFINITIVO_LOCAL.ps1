# ============================================
# DEPLOY DEFINITIVO - CÓDIGO LOCAL
# ============================================
# Este script faz deploy DIRETO do código LOCAL
# Não depende do Cloud Shell ter código atualizado
# ============================================

$ErrorActionPreference = "Stop"

# Cores para output
function Write-Step { param($msg) Write-Host "`n▶ $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✅ $msg" -ForegroundColor Green }
function Write-Error { param($msg) Write-Host "❌ $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "ℹ️  $msg" -ForegroundColor Yellow }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY DEFINITIVO - CÓDIGO LOCAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# CONFIGURAÇÕES
# ============================================
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"
$SECRET_KEY = "django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

Write-Step "Configurações:"
Write-Host "  Projeto: $PROJECT_ID" -ForegroundColor Gray
Write-Host "  Serviço: $SERVICE_NAME" -ForegroundColor Gray
Write-Host "  Região: $REGION" -ForegroundColor Gray
Write-Host ""

# ============================================
# ETAPA 1: VERIFICAÇÕES LOCAIS
# ============================================
Write-Step "ETAPA 1: Verificando código local..."

if (-not (Test-Path "Dockerfile.prod")) {
    Write-Error "Dockerfile.prod não encontrado!"
    exit 1
}
Write-Success "Dockerfile.prod encontrado"

if (-not (Test-Path "manage.py")) {
    Write-Error "manage.py não encontrado! Você está no diretório correto?"
    exit 1
}
Write-Success "manage.py encontrado"

if (-not (Test-Path "sistema_rural/settings_gcp.py")) {
    Write-Error "sistema_rural/settings_gcp.py não encontrado!"
    exit 1
}
Write-Success "settings_gcp.py encontrado"

# Verificar requirements
if (-not (Test-Path "requirements_producao.txt")) {
    Write-Info "requirements_producao.txt não encontrado, criando..."
    if (Test-Path "requirements.txt") {
        Copy-Item "requirements.txt" "requirements_producao.txt"
        Write-Success "Copiado de requirements.txt"
    } else {
        Write-Error "Nenhum arquivo requirements encontrado!"
        exit 1
    }
}

# Garantir openpyxl
$requirementsContent = Get-Content "requirements_producao.txt" -Raw
if ($requirementsContent -notmatch "openpyxl") {
    Write-Info "Adicionando openpyxl ao requirements..."
    Add-Content "requirements_producao.txt" "`nopenpyxl>=3.1.5"
    Write-Success "openpyxl adicionado"
}

Write-Success "Código local verificado!"

# ============================================
# ETAPA 2: AUTENTICAÇÃO GOOGLE CLOUD
# ============================================
Write-Step "ETAPA 2: Autenticando no Google Cloud..."

$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Info "Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na autenticação!"
        exit 1
    }
} else {
    Write-Success "Autenticado: $authCheck"
}

# Configurar projeto
Write-Info "Configurando projeto: $PROJECT_ID"
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro ao configurar projeto!"
    exit 1
}
Write-Success "Projeto configurado"

# ============================================
# ETAPA 3: CORRIGIR SENHA DO BANCO
# ============================================
Write-Step "ETAPA 3: Corrigindo senha do banco..."

gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Senha do banco atualizada"
} else {
    Write-Info "Aviso: Não foi possível atualizar senha (pode ser normal)"
}

# ============================================
# ETAPA 4: BUILD DA IMAGEM (CÓDIGO LOCAL)
# ============================================
Write-Step "ETAPA 4: Buildando imagem Docker (CÓDIGO LOCAL)"
Write-Info "IMPORTANTE: O build vai usar os arquivos DESTE diretório local!"
Write-Info "Isso garante que a versão mais recente seja enviada."
Write-Host ""

$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"

Write-Info "Tag da imagem: $IMAGE_TAG"
Write-Info "Tempo estimado: 5-10 minutos"
Write-Host ""

# Fazer build DIRETO do código local
# O gcloud builds submit envia os arquivos locais para o Cloud Build
Write-Info "Enviando código local para o Cloud Build..."
gcloud builds submit --tag $IMAGE_TAG --timeout=20m --ignore-file=.gcloudignore

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no build!"
    Write-Info "Verifique os logs acima para mais detalhes."
    exit 1
}

Write-Success "Build concluído! Imagem: $IMAGE_TAG"

# ============================================
# ETAPA 5: DEPLOY NO CLOUD RUN
# ============================================
Write-Step "ETAPA 5: Deployando no Cloud Run..."

$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

Write-Info "Variáveis de ambiente configuradas"
Write-Info "Tempo estimado: 2-5 minutos"
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
    --timeout=600 `
    --min-instances=0 `
    --max-instances=10

if ($LASTEXITCODE -ne 0) {
    Write-Error "Erro no deploy!"
    exit 1
}

Write-Success "Deploy concluído!"

# ============================================
# ETAPA 6: OBTER URL E VERIFICAR
# ============================================
Write-Step "ETAPA 6: Obtendo URL do serviço..."

$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1

if ($SERVICE_URL -and -not ($SERVICE_URL -match "ERROR")) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 URL do Serviço:" -ForegroundColor Cyan
    Write-Host "   $SERVICE_URL" -ForegroundColor White
    Write-Host ""
    Write-Host "📋 Credenciais para Login:" -ForegroundColor Cyan
    Write-Host "   Username: admin" -ForegroundColor White
    Write-Host "   Senha: L6171r12@@" -ForegroundColor White
    Write-Host ""
    Write-Host "📦 Imagem criada:" -ForegroundColor Cyan
    Write-Host "   $IMAGE_TAG" -ForegroundColor Gray
    Write-Host ""
    Write-Info "Aguarde 30-60 segundos para o serviço inicializar completamente."
    Write-Info "Depois acesse a URL acima e faça login."
    Write-Host ""
} else {
    Write-Error "Não foi possível obter a URL do serviço!"
    Write-Info "Verifique manualmente no console: https://console.cloud.google.com/run"
}

Write-Host ""
Write-Success "Processo concluído!"


