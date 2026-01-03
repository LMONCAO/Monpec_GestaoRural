# Script para executar collectstatic no Google Cloud Run
# Sistema: Monpec - monpec.com.br

$ErrorActionPreference = "Stop"

# ========================================
# CONFIGURAÇÕES
# ========================================
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$INSTANCE_NAME = "monpec-db"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"
$JOB_NAME = "collectstatic-monpec"

# ========================================
# FUNÇÕES
# ========================================
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Yellow }
function Write-Step { Write-Host ">> $args" -ForegroundColor Blue }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COLECTAR ARQUIVOS ESTATICOS - GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
Write-Step "Verificando gcloud CLI..."
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    Write-Error "gcloud CLI nao encontrado!"
    Write-Info "Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
}
Write-Success "gcloud CLI encontrado!"

# Configurar projeto
Write-Step "Configurando projeto Google Cloud..."
gcloud config set project $PROJECT_ID 2>&1 | Out-Null
Write-Success "Projeto configurado: $PROJECT_ID"

# Verificar se a imagem existe (pular verificação para acelerar)
Write-Step "Pulando verificacao de imagem (assumindo que existe)..."
Write-Info "Se a imagem nao existir, o job falhara e voce pode construir com:"
Write-Host "   gcloud builds submit --tag $IMAGE_NAME" -ForegroundColor Yellow

# Obter connection name do Cloud SQL (se existir)
Write-Step "Verificando Cloud SQL instance..."
$CONNECTION_NAME = $null
$instanceExists = gcloud sql instances describe $INSTANCE_NAME 2>&1
if ($LASTEXITCODE -eq 0) {
    $CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)" 2>&1
    Write-Success "Cloud SQL instance encontrada: $CONNECTION_NAME"
} else {
    Write-Info "Cloud SQL instance nao encontrada. Continuando sem conexao ao banco..."
}

# Preparar variáveis de ambiente
Write-Step "Preparando variaveis de ambiente..."
$ENV_VARS = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp"
)

# Adicionar variáveis do Secret Manager (se existirem)
$secrets = @("DB_PASSWORD", "SECRET_KEY", "MERCADOPAGO_ACCESS_TOKEN", "MERCADOPAGO_PUBLIC_KEY")
foreach ($secret in $secrets) {
    $secretValue = gcloud secrets versions access latest --secret=$secret 2>&1
    if ($LASTEXITCODE -eq 0) {
        $ENV_VARS += "$secret=$secretValue"
        Write-Info "Secret $secret carregado"
    }
}

$ENV_VARS_STRING = $ENV_VARS -join ","

# Criar ou atualizar job
Write-Step "Criando/atualizando job de collectstatic..."

$JOB_ARGS = @(
    "run", "jobs", "create", $JOB_NAME,
    "--image", "$IMAGE_NAME`:latest",
    "--region", $REGION,
    "--set-env-vars", $ENV_VARS_STRING,
    "--memory", "2Gi",
    "--cpu", "1",
    "--max-retries", "3",
    "--task-timeout", "600",
    "--command", "python",
    "--args", "manage.py,collectstatic,--noinput,--clear"
)

if ($CONNECTION_NAME) {
    $JOB_ARGS += "--set-cloudsql-instances"
    $JOB_ARGS += $CONNECTION_NAME
}

try {
    & gcloud $JOB_ARGS --quiet 2>&1 | Out-Null
    Write-Success "Job de collectstatic criado!"
} catch {
    Write-Info "Job ja existe, atualizando..."
    $JOB_ARGS[2] = "update"
    & gcloud $JOB_ARGS --quiet 2>&1 | Out-Null
    Write-Success "Job de collectstatic atualizado!"
}

# Executar job
Write-Step "Executando collectstatic (aguarde, pode levar alguns minutos)..."
Write-Info "Isso pode levar 2-5 minutos..."
Write-Host ""

$execution = gcloud run jobs execute $JOB_NAME --region $REGION --wait 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Success "========================================"
    Write-Success "ARQUIVOS ESTATICOS COLETADOS COM SUCESSO!"
    Write-Success "========================================"
    Write-Host ""
    Write-Info "As imagens agora devem aparecer no site:"
    Write-Host "   https://monpec.com.br/static/site/foto1.jpeg" -ForegroundColor Cyan
    Write-Host "   https://monpec.com.br/static/site/foto2.jpeg" -ForegroundColor Cyan
    Write-Host "   https://monpec.com.br/static/site/foto3.jpeg" -ForegroundColor Cyan
    Write-Host "   https://monpec.com.br/static/site/foto4.jpeg" -ForegroundColor Cyan
    Write-Host "   https://monpec.com.br/static/site/foto5.jpeg" -ForegroundColor Cyan
    Write-Host "   https://monpec.com.br/static/site/foto6.jpeg" -ForegroundColor Cyan
    Write-Host ""
    Write-Info "Verifique os logs do job se precisar:"
    Write-Host "   gcloud run jobs executions list --job=$JOB_NAME --region=$REGION --limit=1" -ForegroundColor Yellow
} else {
    Write-Error "Erro ao executar collectstatic!"
    Write-Info ""
    Write-Info "Verifique os logs do job:"
    Write-Host "   gcloud run jobs executions list --job=$JOB_NAME --region=$REGION --limit=1" -ForegroundColor Yellow
    Write-Host "   gcloud run jobs executions logs read [EXECUTION_NAME] --region=$REGION" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

