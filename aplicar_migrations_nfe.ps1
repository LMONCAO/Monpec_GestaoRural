# Script para aplicar migrations de NF-e
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Aplicando Migrations de NF-e" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mudar para o diretório do script
Set-Location $PSScriptRoot

Write-Host "Verificando migrations pendentes..." -ForegroundColor Yellow
python manage.py showmigrations gestao_rural | Select-String -Pattern "\[ \]"

Write-Host ""
Write-Host "Aplicando migrations..." -ForegroundColor Yellow
python manage.py migrate gestao_rural

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Migrations aplicadas com sucesso!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Erro ao aplicar migrations!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
}

Write-Host ""
Read-Host "Pressione Enter para continuar"






































