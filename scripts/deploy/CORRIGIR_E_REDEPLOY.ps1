# Script para Corrigir o Erro do MercadoPago e Fazer Redeploy

Write-Host "Corrigindo erro do MercadoPago e fazendo redeploy..." -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

$PROJECT_ID = "monpec-sistema-rural"
$SERVICE_NAME = "monpec"
$REGION = "us-central1"
$IMAGE_NAME = "gcr.io/" + $PROJECT_ID + "/" + $SERVICE_NAME + ":latest"

# Configurar projeto
gcloud config set project $PROJECT_ID

Write-Host "1. Verificando se mercadopago esta no requirements_producao.txt..." -ForegroundColor Yellow
if (Select-String -Path "requirements_producao.txt" -Pattern "mercadopago" -Quiet) {
    Write-Host "   mercadopago ja esta no arquivo!" -ForegroundColor Green
} else {
    Write-Host "   Adicionando mercadopago ao requirements_producao.txt..." -ForegroundColor Yellow
    Add-Content -Path "requirements_producao.txt" -Value "`n# Pagamentos`nmercadopago>=2.2.0"
    Write-Host "   mercadopago adicionado!" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. Fazendo build da nova imagem..." -ForegroundColor Yellow
gcloud builds submit --tag $IMAGE_NAME --timeout=600s
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no build!" -ForegroundColor Red
    exit 1
}
Write-Host "Build concluido!" -ForegroundColor Green

Write-Host ""
Write-Host "3. Fazendo deploy..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME --image $IMAGE_NAME --region $REGION --platform managed
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro no deploy!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deploy concluido com sucesso!" -ForegroundColor Green
$serviceUrl = gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>&1
Write-Host "URL do servico: $serviceUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Aguarde alguns segundos e teste a URL novamente!" -ForegroundColor Yellow

