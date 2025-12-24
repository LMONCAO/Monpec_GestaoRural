# Script para atualizar a landing page no Cloud Run
# Força um novo build e deploy para garantir que a versão mais recente seja servida

$ErrorActionPreference = "Stop"

$ProjectId = "monpec-sistema-rural"
$Region = "us-central1"
$ServiceName = "monpec"
$ImageName = "gcr.io/$ProjectId/$ServiceName"
$gcloudPath = "C:\Users\lmonc\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ATUALIZANDO LANDING PAGE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Encontrar diretório do projeto
$projDir = Get-ChildItem -Path "C:\Users\lmonc\Desktop" -Recurse -Directory -ErrorAction SilentlyContinue | 
    Where-Object { $_.Name -eq "Monpec_GestaoRural" } | 
    Select-Object -First 1 -ExpandProperty FullName

if (-not $projDir) {
    Write-Host "❌ Diretório do projeto não encontrado!" -ForegroundColor Red
    exit 1
}

Set-Location $projDir
Write-Host "✅ Diretório: $projDir" -ForegroundColor Green
Write-Host ""

# Verificar template
if (Test-Path "templates\site\landing_page.html") {
    Write-Host "✅ Template encontrado: templates\site\landing_page.html" -ForegroundColor Green
    $content = Get-Content "templates\site\landing_page.html" -Raw
    if ($content -match "GESTÃO RURAL INTELIGENTE" -and $content -match "Controle completo da sua fazenda") {
        Write-Host "✅ Template contém o conteúdo correto" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Template pode não ter o conteúdo esperado" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Template não encontrado!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Build da imagem
Write-Host "🔨 Construindo nova imagem Docker..." -ForegroundColor Yellow
Write-Host "(Isso pode levar alguns minutos...)" -ForegroundColor Gray
Write-Host ""

& $gcloudPath builds submit --tag $ImageName --timeout=30m

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao construir imagem Docker" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Imagem construída com sucesso!" -ForegroundColor Green
Write-Host ""

# Deploy no Cloud Run
Write-Host "🚀 Fazendo deploy no Cloud Run..." -ForegroundColor Yellow
Write-Host ""

& $gcloudPath run deploy $ServiceName `
    --image $ImageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 1Gi `
    --cpu 1 `
    --timeout 300 `
    --max-instances 10 `
    --min-instances 1 `
    --port 8080 `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" `
    --no-traffic

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Erro ao fazer deploy" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Deploy concluído!" -ForegroundColor Green
Write-Host ""

# Migrar tráfego para nova revisão
Write-Host "🔄 Migrando tráfego para nova revisão..." -ForegroundColor Yellow
$latestRevision = & $gcloudPath run revisions list --service $ServiceName --region $Region --limit 1 --format="value(metadata.name)" 2>&1

if ($latestRevision) {
    & $gcloudPath run services update-traffic $ServiceName `
        --region $Region `
        --to-latest
    Write-Host "✅ Tráfego migrado para nova revisão" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ LANDING PAGE ATUALIZADA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$ServiceUrl = & $gcloudPath run services describe $ServiceName --region $Region --format='value(status.url)' 2>&1
Write-Host "URL do Sistema: $ServiceUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Dica: Limpe o cache do navegador (Ctrl+Shift+Delete) ou use modo anônimo para ver a versão atualizada" -ForegroundColor Yellow
Write-Host ""

















