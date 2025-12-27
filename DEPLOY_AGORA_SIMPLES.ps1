# 🚀 DEPLOY SIMPLIFICADO - MONPEC COM MERCADO PAGO
$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "🚀 DEPLOY SIMPLIFICADO - MONPEC" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Configurações
$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"

# Credenciais Mercado Pago
$MERCADOPAGO_TOKEN = "APP_USR-7331944463149248-122310-414426720444c3c1d60cf733585d7821-2581972940"
$MERCADOPAGO_PUBLIC_KEY = "APP_USR-49fe9640-f5b1-4fac-a280-2e28fbd0fea3"

Write-Host "▶ Configurando projeto..." -ForegroundColor Blue
gcloud config set project $PROJECT_ID --quiet 2>&1 | Out-Null

Write-Host "▶ Fazendo build da imagem (pode levar 5-10 minutos)..." -ForegroundColor Blue
gcloud builds submit --tag $IMAGE_NAME`:latest --timeout=600s --quiet 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build concluído!" -ForegroundColor Green
Write-Host ""

# Variáveis de ambiente
$envVars = @(
    "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp",
    "DEBUG=False",
    "MERCADOPAGO_ACCESS_TOKEN=$MERCADOPAGO_TOKEN",
    "MERCADOPAGO_PUBLIC_KEY=$MERCADOPAGO_PUBLIC_KEY",
    "PAYMENT_GATEWAY_DEFAULT=mercadopago",
    "MERCADOPAGO_SUCCESS_URL=https://monpec.com.br/assinaturas/sucesso/",
    "MERCADOPAGO_CANCEL_URL=https://monpec.com.br/assinaturas/cancelado/",
    "PORT=8080",
    "PYTHONUNBUFFERED=1"
)

$envVarsString = $envVars -join ","

Write-Host "▶ Fazendo deploy no Cloud Run..." -ForegroundColor Blue
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME`:latest `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --set-env-vars $envVarsString `
    --memory=2Gi `
    --cpu=2 `
    --timeout=600 `
    --max-instances=10 `
    --min-instances=0 `
    --port=8080 `
    --quiet 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

$serviceUrl = gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)' 2>&1

Write-Host ""
Write-Host "✅ DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 URL do serviço:" -ForegroundColor Cyan
Write-Host "   $serviceUrl" -ForegroundColor Green
Write-Host ""
Write-Host "🔧 Mercado Pago configurado:" -ForegroundColor Cyan
Write-Host "   ✅ Access Token: Configurado" -ForegroundColor Green
Write-Host "   ✅ Public Key: Configurado" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Teste agora:" -ForegroundColor Yellow
Write-Host "   $serviceUrl/assinaturas/" -ForegroundColor Gray
Write-Host ""

