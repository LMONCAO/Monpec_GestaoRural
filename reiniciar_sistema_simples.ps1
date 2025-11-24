# ========================================
# REINICIAR SISTEMA - VERSÃO SIMPLIFICADA
# ========================================
# Este script faz o deploy no Google Cloud Run
# ========================================

Write-Host "REINICIANDO SISTEMA NO GOOGLE CLOUD RUN" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Yellow
Write-Host ""

# Verificar se gcloud esta disponivel
try {
    $gcloudVersion = gcloud --version 2>&1 | Select-Object -First 1
    Write-Host "Google Cloud SDK encontrado" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Google Cloud SDK nao encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "OPCOES:" -ForegroundColor Yellow
    Write-Host "1. Instale o SDK: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    Write-Host "2. Ou use o Cloud Shell:" -ForegroundColor Yellow
    Write-Host "   - Acesse: https://console.cloud.google.com/" -ForegroundColor Cyan
    Write-Host "   - Abra o Cloud Shell" -ForegroundColor Cyan
    Write-Host "   - Execute os comandos manualmente" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Configurar projeto
Write-Host "Configurando projeto Google Cloud..." -ForegroundColor Cyan
gcloud config set project monpec-sistema-rural

# Verificar autenticacao
Write-Host "Verificando autenticacao..." -ForegroundColor Cyan
$authStatus = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
if (-not $authStatus -or $authStatus -match "ERROR") {
    Write-Host "Nao autenticado. Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
}

# Build da imagem
Write-Host ""
Write-Host "Fazendo build da imagem Docker..." -ForegroundColor Cyan
Write-Host "   Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
Write-Host ""

gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec --project=monpec-sistema-rural

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Build falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima para mais detalhes." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Build concluido com sucesso!" -ForegroundColor Green
Write-Host ""

# Obter connection name do banco
Write-Host "Obtendo informacoes do banco de dados..." -ForegroundColor Cyan
$connectionName = gcloud sql instances describe monpec-db --format="value(connectionName)" --project=monpec-sistema-rural 2>&1

if (-not $connectionName -or $connectionName -match "ERROR") {
    Write-Host "AVISO: Nao foi possivel obter connection name do banco" -ForegroundColor Yellow
    Write-Host "   Continuando deploy sem conexao ao banco..." -ForegroundColor Yellow
    $connectionName = $null
}

# Deploy no Cloud Run
Write-Host ""
Write-Host "Fazendo deploy no Cloud Run..." -ForegroundColor Cyan
Write-Host "   Isso pode levar 2-3 minutos..." -ForegroundColor Yellow
Write-Host ""

if ($connectionName) {
    gcloud run deploy monpec `
        --image gcr.io/monpec-sistema-rural/monpec `
        --region us-central1 `
        --platform managed `
        --allow-unauthenticated `
        --project=monpec-sistema-rural `
        --add-cloudsql-instances=$connectionName `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10 `
        --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"
} else {
    gcloud run deploy monpec `
        --image gcr.io/monpec-sistema-rural/monpec `
        --region us-central1 `
        --platform managed `
        --allow-unauthenticated `
        --project=monpec-sistema-rural `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10 `
        --set-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Deploy falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima para mais detalhes." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Deploy concluido com sucesso!" -ForegroundColor Green

# Obter URL do servico
Write-Host ""
Write-Host "Obtendo URL do servico..." -ForegroundColor Cyan
$serviceUrl = gcloud run services describe monpec --region us-central1 --format="value(status.url)" --project=monpec-sistema-rural

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "SISTEMA REINICIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL do sistema: $serviceUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Comandos uteis:" -ForegroundColor Yellow
Write-Host "   Ver logs: gcloud run services logs read monpec --region us-central1 --limit 50" -ForegroundColor Gray
Write-Host "   Ver status: gcloud run services describe monpec --region us-central1" -ForegroundColor Gray
Write-Host ""

