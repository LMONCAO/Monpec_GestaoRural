# 🚀 DEPLOY RÁPIDO - ATUALIZAR SITE MONPEC
# Script simples para fazer deploy das modificações no Google Cloud

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DEPLOY - ATUALIZAR SITE MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se gcloud está instalado
$gcloudPath = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloudPath) {
    Write-Host "❌ Erro: gcloud CLI não está instalado!" -ForegroundColor Red
    Write-Host "   Instale em: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Obter projeto atual
$projectId = gcloud config get-value project 2>$null
if (-not $projectId) {
    Write-Host "❌ Erro: Nenhum projeto Google Cloud configurado!" -ForegroundColor Red
    Write-Host "   Execute: gcloud config set project SEU_PROJECT_ID" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Projeto: $projectId" -ForegroundColor Green
Write-Host ""

# Verificar autenticação
Write-Host "🔐 Verificando autenticação..." -ForegroundColor Yellow
$authCheck = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
if (-not $authCheck) {
    Write-Host "⚠️  Não autenticado. Fazendo login..." -ForegroundColor Yellow
    gcloud auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro na autenticação!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Autenticado: $authCheck" -ForegroundColor Green
Write-Host ""

# Verificar se app.yaml existe
if (-not (Test-Path "app.yaml")) {
    Write-Host "❌ Erro: app.yaml não encontrado!" -ForegroundColor Red
    exit 1
}

# Coletar arquivos estáticos
Write-Host "📦 Coletando arquivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Aviso: Erro ao coletar arquivos estáticos (continuando...)" -ForegroundColor Yellow
}
Write-Host "✅ Arquivos estáticos coletados" -ForegroundColor Green
Write-Host ""

# Deploy no App Engine
Write-Host "🚀 Fazendo deploy no Google App Engine..." -ForegroundColor Yellow
Write-Host "   Isso pode levar alguns minutos..." -ForegroundColor Gray
Write-Host ""

gcloud app deploy app.yaml --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro no deploy!" -ForegroundColor Red
    Write-Host "   Verifique os logs acima para mais detalhes." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "✅ Deploy concluído com sucesso!" -ForegroundColor Green
Write-Host ""

# Obter URL do serviço
$serviceUrl = gcloud app browse --no-launch-browser 2>$null
if ($serviceUrl) {
    Write-Host "🌐 URL do serviço: $serviceUrl" -ForegroundColor Cyan
} else {
    $serviceUrl = "https://$projectId.appspot.com"
    Write-Host "🌐 URL do serviço: $serviceUrl" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Acesse: $serviceUrl" -ForegroundColor White
Write-Host "   2. Verifique se as alterações estão visíveis" -ForegroundColor White
Write-Host "   3. Teste o menu mobile e as imagens na landing page" -ForegroundColor White
Write-Host ""









