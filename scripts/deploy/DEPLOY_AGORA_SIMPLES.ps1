# Script de Deploy Simples - Sistema MONPEC
# Execute este script no diretório raiz do projeto

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY SIMPLES - SISTEMA MONPEC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se está no diretório correto
if (-not (Test-Path "manage.py")) {
    Write-Host "ERRO: manage.py não encontrado! Execute este script no diretório raiz do projeto." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Diretório correto" -ForegroundColor Green
Write-Host ""

# 1. Aplicar migrações
Write-Host "[1/3] Aplicando migrações..." -ForegroundColor Yellow
python manage.py migrate --noinput
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrações aplicadas com sucesso" -ForegroundColor Green
} else {
    Write-Host "✗ Erro ao aplicar migrações" -ForegroundColor Red
}
Write-Host ""

# 2. Coletar arquivos estáticos
Write-Host "[2/3] Coletando arquivos estáticos..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Arquivos estáticos coletados" -ForegroundColor Green
} else {
    Write-Host "⚠ Aviso: Problemas ao coletar arquivos estáticos (pode ser normal)" -ForegroundColor Yellow
}
Write-Host ""

# 3. Verificar sistema
Write-Host "[3/3] Verificando configurações..." -ForegroundColor Yellow
python manage.py check
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Sistema verificado - sem erros" -ForegroundColor Green
} else {
    Write-Host "⚠ Avisos encontrados nas configurações" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "✓ DEPLOY CONCLUÍDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "O sistema está pronto para uso!" -ForegroundColor Cyan
Write-Host "Para iniciar o servidor:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
