# Deploy MONPEC para Google Cloud Run
# Domínio: monpec.com.br

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY MONPEC - Google Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "ERRO: gcloud CLI não encontrado!" -ForegroundColor Red
    Write-Host "Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Verificar autenticação
Write-Host "Verificando autenticação..." -ForegroundColor Yellow
$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $activeAccount) {
    Write-Host "Fazendo login no Google Cloud..." -ForegroundColor Yellow
    gcloud auth login
}

Write-Host ""
Write-Host "Verificando projeto..." -ForegroundColor Yellow
$currentProject = gcloud config get-value project 2>$null
Write-Host "Projeto atual: $currentProject" -ForegroundColor Green

$projectId = Read-Host "Digite o PROJECT_ID do Google Cloud (ou pressione Enter para usar: $currentProject)"
if ([string]::IsNullOrWhiteSpace($projectId)) {
    $projectId = $currentProject
}

Write-Host "Configurando projeto: $projectId" -ForegroundColor Yellow
gcloud config set project $projectId

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. Fazendo build da imagem Docker..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker build -t "gcr.io/$projectId/monpec:latest" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao fazer build da imagem!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "2. Enviando imagem para Container Registry..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker push "gcr.io/$projectId/monpec:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao enviar imagem!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "3. Fazendo deploy no Cloud Run..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

gcloud run deploy monpec `
    --image "gcr.io/$projectId/monpec:latest" `
    --region us-central1 `
    --platform managed `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SITE_URL=https://monpec.com.br" `
    --update-env-vars "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/,MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/" `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --port 8080

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao fazer deploy!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "4. Configurando domínio personalizado..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE: Configure o domínio monpec.com.br no Cloud Run:" -ForegroundColor Yellow
Write-Host "1. Acesse: https://console.cloud.google.com/run" -ForegroundColor White
Write-Host "2. Selecione o serviço 'monpec'" -ForegroundColor White
Write-Host "3. Vá em 'DOMAIN MAPPING'" -ForegroundColor White
Write-Host "4. Adicione: monpec.com.br e www.monpec.com.br" -ForegroundColor White
Write-Host ""
Write-Host "OU execute manualmente:" -ForegroundColor Yellow
Write-Host "gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1" -ForegroundColor White
Write-Host "gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "DEPLOY CONCLUIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE: Configure as variáveis de ambiente no Cloud Run:" -ForegroundColor Yellow
Write-Host "- MERCADOPAGO_ACCESS_TOKEN" -ForegroundColor White
Write-Host "- MERCADOPAGO_PUBLIC_KEY" -ForegroundColor White
Write-Host "- SECRET_KEY" -ForegroundColor White
Write-Host "- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST" -ForegroundColor White
Write-Host ""
Write-Host "Acesse: https://console.cloud.google.com/run/detail/us-central1/monpec" -ForegroundColor Cyan
Write-Host ""



