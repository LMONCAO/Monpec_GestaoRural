# Script para fazer deploy garantindo que Curral V3 está incluído
# Versão sem verificação de Git (usa código já no repositório)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY COM CURRAL V3" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se os arquivos da tela Curral V3 existem localmente
Write-Host "Verificando arquivos da tela Curral V3..." -ForegroundColor Yellow
$arquivosV3 = @(
    "templates\gestao_rural\curral_dashboard_v3.html",
    "gestao_rural\views_curral.py",
    "gestao_rural\urls.py",
    "sistema_rural\urls.py"
)

$arquivosFaltando = @()
foreach ($arquivo in $arquivosV3) {
    if (Test-Path $arquivo) {
        Write-Host "  [OK] $arquivo" -ForegroundColor Green
    } else {
        Write-Host "  [ERRO] $arquivo NÃO ENCONTRADO!" -ForegroundColor Red
        $arquivosFaltando += $arquivo
    }
}

if ($arquivosFaltando.Count -gt 0) {
    Write-Host ""
    Write-Host "ERRO: Alguns arquivos da tela Curral V3 estão faltando!" -ForegroundColor Red
    Write-Host "Não é possível fazer deploy sem esses arquivos." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "IMPORTANTE: Certifique-se de que esses arquivos estão commitados no GitHub!" -ForegroundColor Yellow
    Write-Host "O Cloud Build usa o código do repositório GitHub, não o código local." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Todos os arquivos da tela Curral V3 estão presentes localmente!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  ATENÇÃO: Certifique-se de que esses arquivos estão no GitHub!" -ForegroundColor Yellow
Write-Host "   O Cloud Build usa o código do repositório, não o código local." -ForegroundColor Yellow
Write-Host ""

$resposta = Read-Host "Os arquivos estão commitados no GitHub? (S/N)"
if ($resposta -ne "S" -and $resposta -ne "s" -and $resposta -ne "Y" -and $resposta -ne "y") {
    Write-Host ""
    Write-Host "Por favor, faça commit e push dos arquivos antes de continuar." -ForegroundColor Yellow
    Write-Host "Use GitHub Desktop ou outro cliente Git para fazer isso." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO DEPLOY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "ERRO: Google Cloud CLI não está instalado!" -ForegroundColor Red
    Write-Host "Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Configurar projeto
$PROJECT_ID = "monpec-sistema-rural"
Write-Host "Configurando projeto: $PROJECT_ID" -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
Write-Host ""

# Build
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 1/2: BUILD DA IMAGEM DOCKER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Isso pode levar 10-15 minutos..." -ForegroundColor Yellow
Write-Host "O build usa o código do repositório GitHub." -ForegroundColor Yellow
Write-Host ""

gcloud builds submit --tag gcr.io/$PROJECT_ID/monpec

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Build falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Build concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PASSO 2/2: DEPLOY NO CLOUD RUN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Isso pode levar 2-3 minutos..." -ForegroundColor Yellow
Write-Host ""

# Obter connection name
$CONNECTION_NAME = gcloud sql instances describe monpec-db --format="value(connectionName)" 2>$null

# Gerar SECRET_KEY
$SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>$null
if (-not $SECRET_KEY) {
    $SECRET_KEY = "temp-key-$(Get-Random)"
}

$envVars = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY"

if ($CONNECTION_NAME) {
    $envVars += ",DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=Monpec2025!,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME"
    
    gcloud run deploy monpec `
        --image gcr.io/$PROJECT_ID/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --add-cloudsql-instances $CONNECTION_NAME `
        --set-env-vars $envVars `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
} else {
    gcloud run deploy monpec `
        --image gcr.io/$PROJECT_ID/monpec `
        --platform managed `
        --region us-central1 `
        --allow-unauthenticated `
        --set-env-vars $envVars `
        --memory=512Mi `
        --cpu=1 `
        --timeout=300 `
        --max-instances=10
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Deploy falhou!" -ForegroundColor Red
    Write-Host "Verifique os logs acima" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Obter URL
$SERVICE_URL = gcloud run services describe monpec --region us-central1 --format 'value(status.url)'

Write-Host "========================================" -ForegroundColor Green
Write-Host "  DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "URL do serviço:" -ForegroundColor Cyan
Write-Host "  $SERVICE_URL" -ForegroundColor White
Write-Host ""
Write-Host "Teste a tela Curral V3:" -ForegroundColor Yellow
Write-Host "  $SERVICE_URL/propriedade/1/curral/v3/" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  LEMBRE-SE: Se a tela não aparecer, verifique se os arquivos estão no GitHub!" -ForegroundColor Yellow
Write-Host ""

