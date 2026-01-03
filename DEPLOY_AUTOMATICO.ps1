# Script PowerShell para Deploy Automático no Google Cloud
# Execute: .\DEPLOY_AUTOMATICO.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY AUTOMÁTICO - MONPEC GCP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
Write-Host "[1/7] Verificando Google Cloud SDK..." -ForegroundColor Yellow
try {
    $gcloudVersion = gcloud --version 2>&1
    Write-Host "✅ Google Cloud SDK instalado" -ForegroundColor Green
    Write-Host $gcloudVersion -ForegroundColor Gray
} catch {
    Write-Host "❌ Google Cloud SDK não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Instale o Google Cloud SDK:" -ForegroundColor Yellow
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ou use o Google Cloud Shell:" -ForegroundColor Yellow
    Write-Host "   https://shell.cloud.google.com" -ForegroundColor Cyan
    exit 1
}
Write-Host ""

# Configurar projeto
Write-Host "[2/7] Configurando projeto GCP..." -ForegroundColor Yellow
$PROJECT_ID = "monpec-sistema-rural"
gcloud config set project $PROJECT_ID
Write-Host "✅ Projeto configurado: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Verificar autenticação
Write-Host "[3/7] Verificando autenticação..." -ForegroundColor Yellow
try {
    $auth = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>&1
    if ($auth) {
        Write-Host "✅ Autenticado como: $auth" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Fazendo login..." -ForegroundColor Yellow
        gcloud auth login
    }
} catch {
    Write-Host "⚠️  Erro na autenticação. Execute: gcloud auth login" -ForegroundColor Yellow
}
Write-Host ""

# Habilitar APIs
Write-Host "[4/7] Habilitando APIs necessárias..." -ForegroundColor Yellow
$APIS = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "containerregistry.googleapis.com",
    "sqladmin.googleapis.com"
)

foreach ($api in $APIS) {
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Host "✅ APIs habilitadas" -ForegroundColor Green
Write-Host ""

# Verificar Dockerfile
Write-Host "[5/7] Verificando Dockerfile..." -ForegroundColor Yellow
if (Test-Path "Dockerfile.prod") {
    Write-Host "✅ Dockerfile.prod encontrado" -ForegroundColor Green
    if (-not (Test-Path "Dockerfile")) {
        Copy-Item "Dockerfile.prod" "Dockerfile"
        Write-Host "✅ Dockerfile criado a partir de Dockerfile.prod" -ForegroundColor Green
    }
} elseif (Test-Path "Dockerfile") {
    Write-Host "✅ Dockerfile encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ Dockerfile não encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Build da imagem
Write-Host "[6/7] Buildando imagem Docker..." -ForegroundColor Yellow
Write-Host "⏱️  Isso pode levar 5-10 minutos..." -ForegroundColor Cyan
$IMAGE_TAG = "gcr.io/$PROJECT_ID/monpec:latest"
Write-Host "📦 Executando: gcloud builds submit --tag $IMAGE_TAG" -ForegroundColor Gray
Write-Host ""

gcloud builds submit --tag $IMAGE_TAG

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build concluído!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Deploy no Cloud Run
Write-Host "[7/7] Deployando no Cloud Run..." -ForegroundColor Yellow
Write-Host "⏱️  Isso pode levar 2-5 minutos..." -ForegroundColor Cyan
Write-Host ""

$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$DB_PASSWORD = "L6171r12@@jjms"
$SECRET_KEY = "0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t"

$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

$deployCmd = "gcloud run deploy $SERVICE_NAME " +
    "--image $IMAGE_TAG " +
    "--region=$REGION " +
    "--platform managed " +
    "--allow-unauthenticated " +
    "--add-cloudsql-instances=`"$PROJECT_ID`:$REGION`:monpec-db`" " +
    "--set-env-vars `"$ENV_VARS`" " +
    "--memory=2Gi " +
    "--cpu=2 " +
    "--timeout=600 " +
    "--min-instances=1 " +
    "--max-instances=10 " +
    "--port=8080"

Write-Host "🚀 Executando deploy..." -ForegroundColor Cyan
Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅✅✅ DEPLOY CONCLUÍDO COM SUCESSO! ✅✅✅" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Obter URL
    $SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1
    
    Write-Host "🔗 URL do Serviço:" -ForegroundColor Cyan
    Write-Host "   $SERVICE_URL" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Próximos Passos:" -ForegroundColor Cyan
    Write-Host "   1. Aplicar migrações no Cloud SQL" -ForegroundColor Yellow
    Write-Host "   2. Criar superusuário" -ForegroundColor Yellow
    Write-Host "   3. Testar sistema: $SERVICE_URL" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📊 Ver Logs:" -ForegroundColor Cyan
    Write-Host "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

