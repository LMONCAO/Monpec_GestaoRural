# Script PowerShell Completo para Deploy no Google Cloud
# Execute no diretório do projeto: .\EXECUTAR_DEPLOY_AGORA.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY AUTOMÁTICO - MONPEC GCP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "❌ ERRO: manage.py não encontrado!" -ForegroundColor Red
    Write-Host "Execute este script no diretório raiz do projeto (onde está manage.py)" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Diretório correto detectado" -ForegroundColor Green
Write-Host ""

# Verificar Dockerfile
if (Test-Path "Dockerfile.prod") {
    Write-Host "✅ Dockerfile.prod encontrado" -ForegroundColor Green
    if (-not (Test-Path "Dockerfile")) {
        Copy-Item "Dockerfile.prod" "Dockerfile"
        Write-Host "✅ Dockerfile criado" -ForegroundColor Green
    }
} elseif (Test-Path "Dockerfile") {
    Write-Host "✅ Dockerfile encontrado" -ForegroundColor Green
} else {
    Write-Host "❌ Dockerfile não encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$REGION = "us-central1"
$SERVICE_NAME = "monpec"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

# 1. Configurar projeto
Write-Host "[1/4] Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
Write-Host "✅ Projeto: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# 2. Habilitar APIs
Write-Host "[2/4] Habilitando APIs..." -ForegroundColor Yellow
$APIS = @("cloudbuild.googleapis.com", "run.googleapis.com", "containerregistry.googleapis.com", "sqladmin.googleapis.com")
foreach ($api in $APIS) {
    gcloud services enable $api --quiet 2>&1 | Out-Null
}
Write-Host "✅ APIs habilitadas" -ForegroundColor Green
Write-Host ""

# 3. Build da imagem
Write-Host "[3/4] Buildando imagem Docker..." -ForegroundColor Yellow
Write-Host "⏱️  Isso pode levar 5-10 minutos..." -ForegroundColor Cyan
Write-Host "📦 Enviando para Google Cloud Build..." -ForegroundColor Gray
Write-Host ""

gcloud builds submit --tag $IMAGE_TAG .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}

# 4. Deploy no Cloud Run
Write-Host "[4/4] Deployando no Cloud Run..." -ForegroundColor Yellow
Write-Host "⏱️  Isso pode levar 2-5 minutos..." -ForegroundColor Cyan
Write-Host ""

$DB_PASSWORD = "L6171r12@@jjms"
$SECRET_KEY = "0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_`$1ap4+4t"

$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD,GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

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
    --min-instances=1 `
    --max-instances=10 `
    --port=8080

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅✅✅ DEPLOY CONCLUÍDO! ✅✅✅" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Obter URL
    $SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
    
    Write-Host "🔗 URL do Serviço:" -ForegroundColor Cyan
    Write-Host "   $SERVICE_URL" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 IMPORTANTE - Próximos Passos:" -ForegroundColor Yellow
    Write-Host "   1. Aplicar migrações no Cloud SQL (108 migrações)" -ForegroundColor White
    Write-Host "   2. Testar sistema: $SERVICE_URL" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Ver Logs:" -ForegroundColor Cyan
    Write-Host "   gcloud run services logs read $SERVICE_NAME --region $REGION --limit=50" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}


