# Deploy Rapido - MONPEC
# Adiciona gcloud ao PATH e faz deploy

# Adicionar gcloud ao PATH da sessao atual
$gcloudPaths = @(
    "C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin",
    "$env:USERPROFILE\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
)

foreach ($path in $gcloudPaths) {
    if (Test-Path $path) {
        $env:Path += ";$path"
        break
    }
}

# Verificar gcloud
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    Write-Host "[ERRO] gcloud nao encontrado. Feche e reabra o PowerShell." -ForegroundColor Red
    exit 1
}

Write-Host "Deploy MONPEC - Iniciando..." -ForegroundColor Cyan
Write-Host ""

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Navegar para pasta
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orcamentario\Monpec_GestaoRural"

# Push para GitHub (se houver alteracoes)
Write-Host "Sincronizando com GitHub..." -ForegroundColor Yellow
git add . 2>$null
git commit -m "Deploy automatico" 2>$null
git push origin master 2>$null

# Obter connection name
Write-Host "Obtendo informacoes do banco..." -ForegroundColor Yellow
$CONNECTION_NAME = gcloud sql instances describe monpec-db --format="value(connectionName)" 2>$null

# Gerar SECRET_KEY
$SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
if (-not $SECRET_KEY) {
    $SECRET_KEY = "temp-key-$(Get-Random)"
}

# Build
Write-Host ""
Write-Host "Build da imagem (10-15 min)..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERRO] Build falhou!" -ForegroundColor Red
    exit 1
}

# Deploy
Write-Host ""
Write-Host "Deploy no Cloud Run (2-3 min)..." -ForegroundColor Yellow

if ($CONNECTION_NAME) {
    gcloud run deploy monpec `
        --image gcr.io/monpec-sistema-rural/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --add-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=$SECRET_KEY" `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
} else {
    gcloud run deploy monpec `
        --image gcr.io/monpec-sistema-rural/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY" `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
}

# Obter URL
$URL = gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "DEPLOY CONCLUIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL: $URL" -ForegroundColor Cyan
Write-Host ""

















