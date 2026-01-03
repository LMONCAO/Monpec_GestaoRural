# Script para fazer deploy da correção das imagens
# Remove a rota customizada que estava interferindo com WhiteNoise

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/monpec"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY CORRECAO IMAGENS - GOOGLE CLOUD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Construindo nova imagem Docker..." -ForegroundColor Yellow
Write-Host "(Isso vai executar collectstatic automaticamente)" -ForegroundColor Gray
Write-Host ""

gcloud builds submit --tag $IMAGE_NAME --timeout=600s

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
    Write-Host ""
    
    gcloud run deploy $SERVICE_NAME --image $IMAGE_NAME`:latest --region $REGION
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "DEPLOY CONCLUIDO COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Aguarde alguns segundos e teste as imagens:" -ForegroundColor Cyan
        Write-Host "   https://monpec.com.br/static/site/foto1.jpeg"
        Write-Host "   https://monpec.com.br/static/site/foto2.jpeg"
        Write-Host "   https://monpec.com.br/static/site/foto3.jpeg"
        Write-Host "   https://monpec.com.br/static/site/foto4.jpeg"
        Write-Host "   https://monpec.com.br/static/site/foto5.jpeg"
        Write-Host "   https://monpec.com.br/static/site/foto6.jpeg"
        Write-Host ""
        Write-Host "Se as imagens aparecerem, o problema esta resolvido!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Erro no deploy!" -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "Erro ao construir a imagem!" -ForegroundColor Red
}

Write-Host ""

