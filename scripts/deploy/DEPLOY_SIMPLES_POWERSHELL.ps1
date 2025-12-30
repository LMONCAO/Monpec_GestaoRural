# Script PowerShell SIMPLIFICADO para Deploy
# Execute: .\DEPLOY_SIMPLES_POWERSHELL.ps1

# Configurar variáveis
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$DB_PASSWORD = "L6171r12@@jjms"
$SECRET_KEY = "django-insecure-monpec-sistema-rural-2025-producao-segura-L6171r12@@-YrJOs823th_HB2BP6Uz9A0NVvzL0Fif-t-Rfub5BXgVtE0LxXIWEPQIFqYvI8UNiZKE"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Configurar projeto
Write-Host "Configurando projeto..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID
Write-Host ""

# 2. Corrigir senha do banco
Write-Host "Corrigindo senha do banco..." -ForegroundColor Yellow
gcloud sql users set-password monpec_user --instance=monpec-db --password=$DB_PASSWORD
Write-Host ""

# 3. Build
Write-Host "Buildando imagem (5-10 minutos)..." -ForegroundColor Yellow
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$IMAGE_TAG = "gcr.io/$PROJECT_ID/$SERVICE_NAME`:$TIMESTAMP"
gcloud builds submit --tag $IMAGE_TAG
Write-Host ""

# 4. Deploy
Write-Host "Deployando (2-5 minutos)..." -ForegroundColor Yellow
$ENV_VARS = "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=$SECRET_KEY,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID`:$REGION`:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASSWORD"

gcloud run deploy $SERVICE_NAME --image $IMAGE_TAG --region=$REGION --platform managed --allow-unauthenticated --add-cloudsql-instances="$PROJECT_ID`:$REGION`:monpec-db" --set-env-vars $ENV_VARS --memory=2Gi --cpu=2 --timeout=600
Write-Host ""

# 5. URL
Write-Host "========================================" -ForegroundColor Green
Write-Host "DEPLOY CONCLUIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)"
Write-Host "URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login:" -ForegroundColor Yellow
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Senha: L6171r12@@" -ForegroundColor White
Write-Host ""


