# Script de Deploy para Google Cloud Platform
# Sistema: MONPEC - Monitor da Pecuária

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot + "\.."
Set-Location $ProjectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY PARA GOOGLE CLOUD PLATFORM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "[✓] Google Cloud SDK encontrado" -ForegroundColor Green
} catch {
    Write-Host "[✗] Google Cloud SDK não encontrado!" -ForegroundColor Red
    Write-Host "    Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verificar se está autenticado
try {
    gcloud auth list --filter=status:ACTIVE --format="value(account)" | Out-Null
    Write-Host "[✓] Autenticado no Google Cloud" -ForegroundColor Green
} catch {
    Write-Host "[✗] Não autenticado no Google Cloud!" -ForegroundColor Red
    Write-Host "    Execute: gcloud auth login" -ForegroundColor Yellow
    exit 1
}

# Solicitar informações do projeto
Write-Host ""
Write-Host "Configuração do Deploy:" -ForegroundColor Cyan
$ProjectId = Read-Host "ID do Projeto GCP"
$Region = Read-Host "Região (ex: us-central1, southamerica-east1)" 
if ([string]::IsNullOrWhiteSpace($Region)) {
    $Region = "southamerica-east1"
}

$ServiceName = Read-Host "Nome do serviço Cloud Run (ex: monpec-gestao-rural)"
if ([string]::IsNullOrWhiteSpace($ServiceName)) {
    $ServiceName = "monpec-gestao-rural"
}

Write-Host ""
Write-Host "Opções de Deploy:" -ForegroundColor Cyan
Write-Host "1. Cloud Run (Recomendado - Containerizado)"
Write-Host "2. App Engine (Tradicional)"
$DeployOption = Read-Host "Escolha (1 ou 2)"

# Definir projeto
Write-Host ""
Write-Host "[1/5] Configurando projeto GCP..." -ForegroundColor Yellow
gcloud config set project $ProjectId
Write-Host "  [✓] Projeto configurado: $ProjectId" -ForegroundColor Green

# Habilitar APIs necessárias
Write-Host ""
Write-Host "[2/5] Habilitando APIs necessárias..." -ForegroundColor Yellow
$Apis = @(
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $Apis) {
    try {
        gcloud services enable $api --quiet 2>&1 | Out-Null
        Write-Host "  [✓] API $api habilitada" -ForegroundColor Green
    } catch {
        Write-Host "  [!] API $api pode já estar habilitada" -ForegroundColor Yellow
    }
}

# Coletar arquivos estáticos
Write-Host ""
Write-Host "[3/5] Coletando arquivos estáticos..." -ForegroundColor Yellow
try {
    python manage.py collectstatic --noinput
    Write-Host "  [✓] Arquivos estáticos coletados" -ForegroundColor Green
} catch {
    Write-Host "  [!] Erro ao coletar estáticos: $_" -ForegroundColor Yellow
}

# Fazer backup antes do deploy
Write-Host ""
Write-Host "[4/5] Criando backup antes do deploy..." -ForegroundColor Yellow
try {
    & "$PSScriptRoot\BACKUP_SISTEMA.ps1"
    Write-Host "  [✓] Backup criado" -ForegroundColor Green
} catch {
    Write-Host "  [!] Erro ao criar backup: $_" -ForegroundColor Yellow
}

# Deploy
Write-Host ""
Write-Host "[5/5] Fazendo deploy..." -ForegroundColor Yellow

if ($DeployOption -eq "1") {
    # Cloud Run
    Write-Host "  Deployando no Cloud Run..." -ForegroundColor Cyan
    
    # Verificar se Dockerfile existe
    if (-not (Test-Path "Dockerfile")) {
        Write-Host "  [✗] Dockerfile não encontrado!" -ForegroundColor Red
        Write-Host "  Criando Dockerfile básico..." -ForegroundColor Yellow
        
        # Criar Dockerfile básico
        $DockerfileContent = @"
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD exec gunicorn sistema_rural.wsgi:application --bind 0.0.0.0:8080 --workers 4 --threads 2
"@
        $DockerfileContent | Out-File "Dockerfile" -Encoding UTF8
        Write-Host "  [✓] Dockerfile criado" -ForegroundColor Green
    }
    
    # Fazer build e deploy
    try {
        gcloud run deploy $ServiceName `
            --source . `
            --region $Region `
            --platform managed `
            --allow-unauthenticated `
            --memory 1Gi `
            --cpu 1 `
            --timeout 300 `
            --max-instances 10
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "URL do serviço:" -ForegroundColor Yellow
        gcloud run services describe $ServiceName --region $Region --format="value(status.url)"
        Write-Host ""
    } catch {
        Write-Host "  [✗] Erro no deploy: $_" -ForegroundColor Red
        exit 1
    }
    
} else {
    # App Engine
    Write-Host "  Deployando no App Engine..." -ForegroundColor Cyan
    
    # Verificar se app.yaml existe
    if (-not (Test-Path "app.yaml")) {
        if (Test-Path "deploy\config\app.yaml") {
            Copy-Item "deploy\config\app.yaml" "app.yaml"
            Write-Host "  [✓] app.yaml copiado" -ForegroundColor Green
        } else {
            Write-Host "  [✗] app.yaml não encontrado!" -ForegroundColor Red
            exit 1
        }
    }
    
    try {
        gcloud app deploy --quiet
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "URL do serviço:" -ForegroundColor Yellow
        gcloud app browse
        Write-Host ""
    } catch {
        Write-Host "  [✗] Erro no deploy: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Configurar variáveis de ambiente no GCP Console" -ForegroundColor White
Write-Host "2. Configurar banco de dados (Cloud SQL recomendado)" -ForegroundColor White
Write-Host "3. Configurar domínio personalizado (opcional)" -ForegroundColor White
Write-Host "4. Testar todas as funcionalidades" -ForegroundColor White
Write-Host ""






