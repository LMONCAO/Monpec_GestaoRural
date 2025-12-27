# 🔄 REDEPLOY COM CORREÇÕES - MONPEC
# Atualiza o serviço Cloud Run com as correções mais recentes

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔄 REDEPLOY COM CORREÇÕES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar serviço atual
Write-Host "Verificando serviço atual..." -ForegroundColor Cyan
$SERVICE_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1
Write-Host "URL atual: $SERVICE_URL" -ForegroundColor Green
Write-Host ""

# Obter connection name do Cloud SQL
Write-Host "Obtendo informações do Cloud SQL..." -ForegroundColor Cyan
$INSTANCE_NAME = "monpec-db"
$CONNECTION_NAME = gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)" 2>&1
Write-Host "Connection name: $CONNECTION_NAME" -ForegroundColor Green
Write-Host ""

# Fazer build da nova imagem
Write-Host "Fazendo build da nova imagem (5-10 minutos)..." -ForegroundColor Cyan
gcloud builds submit --tag $IMAGE_NAME --timeout=600s
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build concluído!" -ForegroundColor Green
Write-Host ""

# Obter variáveis de ambiente atuais
Write-Host "Obtendo variáveis de ambiente atuais..." -ForegroundColor Cyan
$CURRENT_ENV = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>&1

# Redeploy com nova imagem
Write-Host "Fazendo redeploy com nova imagem..." -ForegroundColor Cyan
gcloud run deploy $SERVICE_NAME `
    --image $IMAGE_NAME `
    --region $REGION `
    --add-cloudsql-instances $CONNECTION_NAME `
    --quiet 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Redeploy concluído com sucesso!" -ForegroundColor Green
} else {
    Write-Host "❌ Erro no redeploy!" -ForegroundColor Red
    exit 1
}

$NEW_URL = gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)" 2>&1
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ REDEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Nova URL: $NEW_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "Teste acessando: $NEW_URL" -ForegroundColor Yellow
Write-Host ""










