# Solução FINAL para as imagens - Deploy com rota customizada como fallback

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOLUCAO FINAL - IMAGENS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Esta solucao adiciona rota customizada como FALLBACK" -ForegroundColor Yellow
Write-Host "Se WhiteNoise falhar, a view customizada serve os arquivos" -ForegroundColor Yellow
Write-Host ""

Write-Host "Construindo nova imagem..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_NAME --timeout=600s

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Fazendo deploy..." -ForegroundColor Yellow
    gcloud run deploy $SERVICE_NAME --image $IMAGE_NAME`:latest --region $REGION
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "DEPLOY CONCLUIDO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Aguarde 30 segundos e teste:" -ForegroundColor Cyan
        Write-Host "   https://monpec.com.br/static/site/foto1.jpeg"
        Write-Host ""
        Write-Host "Se ainda nao funcionar, acesse:" -ForegroundColor Yellow
        Write-Host "   https://monpec.com.br/debug/static-files/" -ForegroundColor Yellow
        Write-Host "   (para verificar se os arquivos existem no servidor)"
    }
} else {
    Write-Host "Erro no build!" -ForegroundColor Red
}

Write-Host ""


