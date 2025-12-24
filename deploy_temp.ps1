# Script temporário para deploy
$ErrorActionPreference = "Stop"

# Definir diretório do projeto
$projectDir = "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Navegar para o diretório do projeto
Set-Location $projectDir

Write-Host "Diretório atual: $(Get-Location)" -ForegroundColor Cyan

# Verificar se Dockerfile existe
if (-not (Test-Path "Dockerfile")) {
    Write-Host "❌ Dockerfile não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dockerfile encontrado!" -ForegroundColor Green

# Configurar projeto
$Projeto = "monpec-sistema-rural"
$Regiao = "us-central1"
$Servico = "monpec"
$imageTag = "gcr.io/$Projeto/$Servico"

Write-Host "🔨 Fazendo build da imagem Docker..." -ForegroundColor Yellow
gcloud builds submit --tag $imageTag --timeout=30m

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no build!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build concluído!" -ForegroundColor Green

Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $Servico `
    --image $imageTag `
    --platform managed `
    --region $Regiao `
    --allow-unauthenticated `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
    --memory=1Gi `
    --cpu=1 `
    --timeout=300 `
    --max-instances=10 `
    --min-instances=1 `
    --port=8080

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deploy concluído!" -ForegroundColor Green

$serviceUrl = gcloud run services describe $Servico --region $Regiao --format='value(status.url)'
Write-Host "🌐 URL do serviço: $serviceUrl" -ForegroundColor Cyan
















