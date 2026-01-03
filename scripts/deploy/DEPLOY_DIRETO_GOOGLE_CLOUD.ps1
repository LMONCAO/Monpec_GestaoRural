# Script para Deploy Direto no Google Cloud Run
# Este script faz deploy direto sem depender do Git
# Execute no Google Cloud SDK Shell ou PowerShell com gcloud instalado

Write-Host "Deploy Direto para Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuracoes (ajuste conforme necessario)
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/" + $PROJECT_ID + "/" + $SERVICE_NAME + ":latest"

# Verificar se esta no diretorio correto
$currentDir = Get-Location
Write-Host "Diretorio atual: $currentDir" -ForegroundColor Yellow

if (-not (Test-Path "Dockerfile.prod")) {
    Write-Host "ERRO: Dockerfile.prod nao encontrado!" -ForegroundColor Red
    Write-Host "   Certifique-se de estar no diretorio do projeto." -ForegroundColor Red
    exit 1
}

# Verificar autenticacao
Write-Host ""
Write-Host "Verificando autenticacao..." -ForegroundColor Yellow
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authCheck -or $authCheck -match "ERROR") {
    Write-Host "Nao autenticado. Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Falha na autenticacao!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Autenticado como: $authCheck" -ForegroundColor Green
}

# Configurar projeto
Write-Host ""
Write-Host "Configurando projeto: $PROJECT_ID" -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao configurar projeto!" -ForegroundColor Red
    exit 1
}
Write-Host "Projeto configurado!" -ForegroundColor Green

# Habilitar APIs necessarias (silencioso)
Write-Host ""
Write-Host "Habilitando APIs necessarias..." -ForegroundColor Yellow
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com"
)

foreach ($api in $apis) {
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Host "APIs habilitadas!" -ForegroundColor Green

# Build da imagem usando Cloud Build
Write-Host ""
Write-Host "Fazendo build da imagem Docker..." -ForegroundColor Yellow
Write-Host "   Isso pode levar alguns minutos..." -ForegroundColor Gray

# Usar Dockerfile.prod se existir, senao usar Dockerfile
$dockerfile = "Dockerfile.prod"
if (-not (Test-Path $dockerfile)) {
    $dockerfile = "Dockerfile"
    if (-not (Test-Path $dockerfile)) {
        Write-Host "Nenhum Dockerfile encontrado!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "   Usando: $dockerfile" -ForegroundColor Gray

# Build usando gcloud builds submit
gcloud builds submit --tag $IMAGE_NAME --timeout=600s
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no build da imagem!" -ForegroundColor Red
    exit 1
}
Write-Host "Build concluido com sucesso!" -ForegroundColor Green

# Deploy no Cloud Run
Write-Host ""
Write-Host "Fazendo deploy no Cloud Run..." -ForegroundColor Yellow

# Verificar se o servico ja existe
$serviceExists = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(name)" 2>&1

if ($serviceExists -and -not ($serviceExists -match "ERROR")) {
    Write-Host "   Servico existente encontrado. Atualizando..." -ForegroundColor Gray
    $deployCmd = "gcloud run deploy $SERVICE_NAME --image $IMAGE_NAME --region $REGION --platform managed"
} else {
    Write-Host "   Criando novo servico..." -ForegroundColor Gray
    $deployCmd = "gcloud run deploy $SERVICE_NAME --image $IMAGE_NAME --region $REGION --platform managed --allow-unauthenticated"
}

# Executar deploy
Invoke-Expression $deployCmd
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no deploy!" -ForegroundColor Red
    exit 1
}

# Obter URL do servico
Write-Host ""
Write-Host "Obtendo URL do servico..." -ForegroundColor Yellow
$serviceUrl = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1

if ($serviceUrl -and -not ($serviceUrl -match "ERROR")) {
    Write-Host ""
    Write-Host "Deploy concluido com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "URL do servico: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Proximos passos:" -ForegroundColor Yellow
    Write-Host "   1. Configure as variaveis de ambiente no Cloud Run Console" -ForegroundColor Gray
    Write-Host "   2. Execute as migracoes do Django" -ForegroundColor Gray
    Write-Host "   3. Crie um superusuario" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Para configurar variaveis de ambiente:" -ForegroundColor Yellow
    $envVarsCmd = "gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars=DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"
    Write-Host "   $envVarsCmd" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "Deploy concluido, mas nao foi possivel obter a URL." -ForegroundColor Yellow
    Write-Host "   Verifique no console: https://console.cloud.google.com/run" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Processo concluido!" -ForegroundColor Green
