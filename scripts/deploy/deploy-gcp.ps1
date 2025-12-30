# Script de Deploy Otimizado para Google Cloud Run - Sistema MONPEC
# Versão PowerShell para Windows
# Execute: .\deploy-gcp.ps1

param(
    [string]$ProjectId = "",
    [string]$ServiceName = "monpec",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

# Cores para output
function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Warning { Write-Host "⚠ $args" -ForegroundColor Yellow }
function Write-Info { Write-Host "→ $args" -ForegroundColor Cyan }
function Write-Step { Write-Host "▶ $args" -ForegroundColor Blue }

Write-Host ""
Write-Host "========================================"
Write-Host "  DEPLOY GOOGLE CLOUD - SISTEMA MONPEC"
Write-Host "========================================"
Write-Host ""

# Configurações
if ([string]::IsNullOrEmpty($ProjectId)) {
    $ProjectId = $env:GCP_PROJECT
    if ([string]::IsNullOrEmpty($ProjectId)) {
        try {
            $ProjectId = gcloud config get-value project 2>$null
        } catch {
            $ProjectId = ""
        }
    }
}

$ImageName = "gcr.io/$ProjectId/$ServiceName"

# Verificar se gcloud está instalado
Write-Step "Verificando gcloud CLI..."
try {
    $null = Get-Command gcloud -ErrorAction Stop
    Write-Success "gcloud CLI encontrado"
} catch {
    Write-Error "gcloud CLI não está instalado!"
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
}

# Verificar autenticação
Write-Step "Verificando autenticação..."
$authList = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if ([string]::IsNullOrEmpty($authList)) {
    Write-Warning "Não autenticado. Fazendo login..."
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na autenticação!"
        exit 1
    }
}
Write-Success "Autenticado"

# Configurar projeto
if ([string]::IsNullOrEmpty($ProjectId)) {
    Write-Error "PROJECT_ID não definido!"
    Write-Host "Defina com: `$env:GCP_PROJECT='seu-projeto-id'"
    Write-Host "Ou configure com: gcloud config set project SEU-PROJETO-ID"
    exit 1
}

Write-Step "Configurando projeto: $ProjectId"
gcloud config set project $ProjectId --quiet
Write-Success "Projeto configurado"

# Habilitar APIs necessárias
Write-Step "Habilitando APIs necessárias..."
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    gcloud services enable $api --quiet 2>$null
}
Write-Success "APIs habilitadas"

# Verificar Dockerfile
Write-Step "Verificando Dockerfile..."
if (-not (Test-Path "Dockerfile.prod")) {
    Write-Error "Dockerfile.prod não encontrado!"
    exit 1
}
Write-Success "Dockerfile.prod encontrado"

# Verificar requirements.txt
if (-not (Test-Path "requirements.txt")) {
    Write-Error "requirements.txt não encontrado!"
    exit 1
}

# Build da imagem Docker
Write-Step "Fazendo build da imagem Docker..."
Write-Info "  Imagem: ${ImageName}:latest"
Write-Info "  Isso pode levar alguns minutos..."

gcloud builds submit --tag "${ImageName}:latest" --timeout=20m --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Success "Build concluído com sucesso"
} else {
    Write-Error "Erro no build da imagem!"
    exit 1
}

# Verificar variáveis de ambiente
Write-Step "Verificando variáveis de ambiente..."

# Construir lista de variáveis de ambiente
$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

if (-not [string]::IsNullOrEmpty($env:SECRET_KEY)) {
    $envVars += ",SECRET_KEY=$env:SECRET_KEY"
} else {
    Write-Warning "SECRET_KEY não definida"
}

if (-not [string]::IsNullOrEmpty($env:DB_NAME)) { $envVars += ",DB_NAME=$env:DB_NAME" }
if (-not [string]::IsNullOrEmpty($env:DB_USER)) { $envVars += ",DB_USER=$env:DB_USER" }
if (-not [string]::IsNullOrEmpty($env:DB_PASSWORD)) { $envVars += ",DB_PASSWORD=$env:DB_PASSWORD" }
if (-not [string]::IsNullOrEmpty($env:DB_HOST)) { $envVars += ",DB_HOST=$env:DB_HOST" }
if (-not [string]::IsNullOrEmpty($env:CLOUD_SQL_CONNECTION_NAME)) {
    $envVars += ",CLOUD_SQL_CONNECTION_NAME=$env:CLOUD_SQL_CONNECTION_NAME"
}

# Deploy no Cloud Run
Write-Step "Fazendo deploy no Cloud Run..."
Write-Info "  Serviço: $ServiceName"
Write-Info "  Região: $Region"
Write-Info "  Imagem: ${ImageName}:latest"

$deployArgs = @(
    "run", "deploy", $ServiceName,
    "--image", "${ImageName}:latest",
    "--platform", "managed",
    "--region", $Region,
    "--allow-unauthenticated",
    "--set-env-vars", $envVars,
    "--memory", "2Gi",
    "--cpu", "2",
    "--timeout", "300",
    "--max-instances", "10",
    "--min-instances", "1",
    "--port", "8080"
)

# Adicionar Cloud SQL connection se definida
if (-not [string]::IsNullOrEmpty($env:CLOUD_SQL_CONNECTION_NAME)) {
    $deployArgs += "--add-cloudsql-instances"
    $deployArgs += $env:CLOUD_SQL_CONNECTION_NAME
    Write-Info "  Cloud SQL: $env:CLOUD_SQL_CONNECTION_NAME"
}

& gcloud $deployArgs --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Success "Deploy no Cloud Run concluído!"
} else {
    Write-Error "Erro no deploy!"
    exit 1
}

# Obter URL do serviço
Write-Step "Obtendo URL do serviço..."
$serviceUrl = gcloud run services describe $ServiceName --region=$Region --format="value(status.url)" 2>$null
if (-not [string]::IsNullOrEmpty($serviceUrl)) {
    Write-Success "Serviço disponível em: $serviceUrl"
} else {
    Write-Warning "Não foi possível obter a URL do serviço"
}

# Executar migrações via job
Write-Step "Aplicando migrações do banco de dados..."
$jobName = "migrate-monpec"

# Verificar se job já existe
$jobExists = $false
gcloud run jobs describe $jobName --region=$Region 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    $jobExists = $true
    Write-Info "Job de migração já existe. Executando..."
    
    gcloud run jobs execute $jobName --region=$Region --wait
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Migrações aplicadas com sucesso!"
    } else {
        Write-Warning "Erro ao executar migrações. Tente executar manualmente:"
        Write-Info "  gcloud run jobs execute $jobName --region=$Region"
    }
} else {
    Write-Info "Criando job de migração..."
    
    $jobArgs = @(
        "run", "jobs", "create", $jobName,
        "--image", "${ImageName}:latest",
        "--region", $Region,
        "--set-env-vars", $envVars,
        "--memory", "2Gi",
        "--cpu", "1",
        "--max-retries", "3",
        "--task-timeout", "600",
        "--command", "python",
        "--args", "manage.py,migrate,--noinput"
    )
    
    if (-not [string]::IsNullOrEmpty($env:CLOUD_SQL_CONNECTION_NAME)) {
        $jobArgs += "--set-cloudsql-instances"
        $jobArgs += $env:CLOUD_SQL_CONNECTION_NAME
    }
    
    & gcloud $jobArgs --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Job de migração criado"
        gcloud run jobs execute $jobName --region=$Region --wait
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Migrações aplicadas com sucesso!"
        } else {
            Write-Warning "Erro ao executar migrações. Tente executar manualmente:"
            Write-Info "  gcloud run jobs execute $jobName --region=$Region"
        }
    } else {
        Write-Warning "Não foi possível criar job de migração"
        Write-Info "Execute as migrações manualmente após o deploy"
    }
}

# Resumo final
Write-Host ""
Write-Host "========================================"
Write-Success "DEPLOY CONCLUÍDO COM SUCESSO!"
Write-Host "========================================"
Write-Host ""
Write-Host "📋 Informações:"
Write-Host "  • Serviço: $ServiceName"
if (-not [string]::IsNullOrEmpty($serviceUrl)) {
    Write-Host "  • URL: $serviceUrl"
}
Write-Host "  • Região: $Region"
Write-Host "  • Projeto: $ProjectId"
Write-Host ""
Write-Host "🔗 Próximos passos:"
Write-Host "  1. Verifique os logs:"
Write-Host "     gcloud run services logs read $ServiceName --region=$Region --limit=50"
Write-Host ""
if (-not [string]::IsNullOrEmpty($serviceUrl)) {
    Write-Host "  2. Teste o acesso em: $serviceUrl"
    Write-Host ""
}
Write-Host "  3. Se necessário, configure variáveis de ambiente adicionais:"
Write-Host "     gcloud run services update $ServiceName --region=$Region --update-env-vars KEY=VALUE"
Write-Host ""
Write-Host "  4. Para executar migrações manualmente:"
Write-Host "     gcloud run jobs execute $jobName --region=$Region"
Write-Host ""

