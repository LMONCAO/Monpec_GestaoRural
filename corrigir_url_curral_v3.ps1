# ========================================
# CORRIGIR URL CURRAL V3 - REINICIAR SERVIDOR
# ========================================

Write-Host "CORRIGINDO URL CURRAL V3" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Yellow
Write-Host ""

# Verificar se estamos no diretorio correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: Execute este script na raiz do projeto Django!" -ForegroundColor Red
    exit 1
}

# Verificar se a URL esta configurada
Write-Host "1. Verificando configuracao da URL..." -ForegroundColor Cyan
$urlsContent = Get-Content "sistema_rural\urls.py" -Raw
if ($urlsContent -match "curral/v3/") {
    Write-Host "   URL v3 encontrada em sistema_rural/urls.py" -ForegroundColor Green
} else {
    Write-Host "   ERRO: URL v3 nao encontrada!" -ForegroundColor Red
    exit 1
}

# Verificar se a view existe
Write-Host ""
Write-Host "2. Verificando view curral_dashboard_v3..." -ForegroundColor Cyan
$viewsContent = Get-Content "gestao_rural\views_curral.py" -Raw
if ($viewsContent -match "def curral_dashboard_v3") {
    Write-Host "   View curral_dashboard_v3 encontrada!" -ForegroundColor Green
} else {
    Write-Host "   ERRO: View nao encontrada!" -ForegroundColor Red
    exit 1
}

# Limpar cache
Write-Host ""
Write-Host "3. Limpando cache..." -ForegroundColor Cyan
Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "   Cache limpo!" -ForegroundColor Green

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "REINICIE O SERVIDOR DJANGO:" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. Pare o servidor atual (Ctrl+C no terminal)" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Inicie o servidor novamente:" -ForegroundColor Yellow
Write-Host "   python manage.py runserver" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Acesse a URL:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/propriedade/2/curral/v3/" -ForegroundColor Green
Write-Host "   (Substitua '2' pelo ID da sua propriedade)" -ForegroundColor Gray
Write-Host ""
Write-Host "OU use a URL do painel (que redireciona para v3):" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/propriedade/2/curral/painel/" -ForegroundColor Cyan
Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "VERIFICACAO:" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Apos reiniciar, a URL /curral/v3/ deve funcionar!" -ForegroundColor Green
Write-Host ""

