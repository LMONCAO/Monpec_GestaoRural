# Script para verificar status do serviço Cloud Run
# Execute: .\VERIFICAR_STATUS.ps1

$SERVICE_NAME = "monpec"
$REGION = "us-central1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 VERIFICANDO STATUS DO SERVIÇO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se o serviço existe
Write-Host "📋 Listando serviços..." -ForegroundColor Yellow
gcloud run services list --region=$REGION
Write-Host ""

# 2. Ver status detalhado
Write-Host "📊 Status detalhado do serviço..." -ForegroundColor Yellow
$SERVICE_STATUS = gcloud run services describe $SERVICE_NAME --region=$REGION --format="yaml(status.conditions,status.url)" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host $SERVICE_STATUS -ForegroundColor White
} else {
    Write-Host "❌ Serviço não encontrado ou erro ao acessar" -ForegroundColor Red
    Write-Host $SERVICE_STATUS -ForegroundColor Red
}
Write-Host ""

# 3. Obter URL
Write-Host "🔗 Obtendo URL do serviço..." -ForegroundColor Yellow
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1
if ($SERVICE_URL -and $SERVICE_URL -notmatch "ERROR") {
    Write-Host "✅ URL: $SERVICE_URL" -ForegroundColor Green
} else {
    Write-Host "❌ Não foi possível obter a URL" -ForegroundColor Red
}
Write-Host ""

# 4. Ver logs de erro
Write-Host "📋 Últimos logs de erro..." -ForegroundColor Yellow
$ERROR_LOGS = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME AND severity>=ERROR" --limit=10 --format="table(timestamp,severity,textPayload)" 2>&1
if ($ERROR_LOGS) {
    Write-Host $ERROR_LOGS -ForegroundColor Red
} else {
    Write-Host "✅ Nenhum erro encontrado nos logs recentes" -ForegroundColor Green
}
Write-Host ""

# 5. Ver últimos logs gerais
Write-Host "📋 Últimos logs gerais..." -ForegroundColor Yellow
$GENERAL_LOGS = gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" --limit=10 --format="value(textPayload)" 2>&1
if ($GENERAL_LOGS) {
    Write-Host ($GENERAL_LOGS | Select-Object -Last 5) -ForegroundColor White
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Verificação concluída" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan


