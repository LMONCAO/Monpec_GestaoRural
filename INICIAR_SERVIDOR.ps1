# Script PowerShell para iniciar o servidor Django
Write-Host "Iniciando servidor Django..." -ForegroundColor Green

# Navegar para o diretório do projeto
Set-Location $PSScriptRoot

# Verificar se o Python está disponível
try {
    $pythonVersion = python --version
    Write-Host "Python detectado: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Erro: Python não encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar se o manage.py existe
if (-not (Test-Path "manage.py")) {
    Write-Host "Erro: manage.py não encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar configurações do Django
Write-Host "Verificando configurações..." -ForegroundColor Yellow
python manage.py check
if ($LASTEXITCODE -ne 0) {
    Write-Host "Aviso: Verificação do Django encontrou problemas" -ForegroundColor Yellow
}

# Iniciar servidor
Write-Host "`nIniciando servidor na porta 8000..." -ForegroundColor Green
Write-Host "Acesse: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Pressione Ctrl+C para parar o servidor`n" -ForegroundColor Yellow

python manage.py runserver 8000
